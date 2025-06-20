from __future__ import annotations

import json
import logging
from datetime import datetime
from time import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from . import deps, models
from .database import SessionLocal

logger = logging.getLogger("audit")

ROLE_LIMITS = {
    "Gerente de servicios": 1000,
    "Analista de Pruebas con skill de automatizaci\u00f3n": 500,
    "Automatizador de Pruebas": 500,
}
WINDOW_SECONDS = 3600
_rate_limits: dict[int, list[float]] = {}


class WorkspaceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            try:
                payload = jwt.decode(token, deps.SECRET_KEY, algorithms=[deps.ALGORITHM])
                user_id = payload.get("user_id")
                if user_id is None:
                    raise ValueError
            except Exception:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
            db = SessionLocal()
            try:
                user = db.query(models.User).filter(models.User.id == user_id).first()
                if not user:
                    return JSONResponse(status_code=401, content={"detail": "User not found"})
                role_name = user.role.name if user.role else ""
                limit = ROLE_LIMITS.get(role_name)
                if limit:
                    now = time()
                    timestamps = [t for t in _rate_limits.get(user.id, []) if now - t < WINDOW_SECONDS]
                    if len(timestamps) >= limit:
                        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                    timestamps.append(now)
                    _rate_limits[user.id] = timestamps
                request.state.user = user

                client_id = request.headers.get("X-Client-ID")
                project_id = request.headers.get("X-Project-ID")
                if client_id:
                    try:
                        cid = int(client_id)
                    except ValueError:
                        return JSONResponse(status_code=400, content={"detail": "Invalid client_id"})
                    if not deps.can_access_client(db, user.id, cid):
                        return JSONResponse(status_code=403, content={"detail": "Client access denied"})
                    request.state.client_id = cid
                if project_id:
                    try:
                        pid = int(project_id)
                    except ValueError:
                        return JSONResponse(status_code=400, content={"detail": "Invalid project_id"})
                    if not deps.can_access_project(db, user.id, pid):
                        return JSONResponse(status_code=403, content={"detail": "Project access denied"})
                    request.state.project_id = pid
            finally:
                db.close()
        return await call_next(request)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body_bytes = await request.body()
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        req = Request(request.scope, receive)
        response = await call_next(req)

        user = getattr(request.state, "user", None)
        user_name = user.username if user else None
        client_id = getattr(request.state, "client_id", None)
        project_id = getattr(request.state, "project_id", None)
        payload = None
        try:
            data = json.loads(body_bytes.decode()) if body_bytes else None
            if isinstance(data, dict):
                data.pop("password", None)
                data.pop("hashed_password", None)
            payload = data
        except Exception:
            payload = None
        logger.info(
            "user=%s endpoint=%s timestamp=%s client=%s project=%s payload=%s",
            user_name,
            request.url.path,
            datetime.utcnow().isoformat(),
            client_id,
            project_id,
            payload,
        )
        db = SessionLocal()
        try:
            event = models.AuditEvent(
                user_id=user.id if user else None,
                endpoint=request.url.path,
                client_id=client_id,
                project_id=project_id,
                payload=json.dumps(payload) if payload is not None else None,
            )
            db.add(event)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
        return response


def setup_gateway(app: FastAPI) -> None:
    app.add_middleware(WorkspaceMiddleware)
    app.add_middleware(AuditMiddleware)


