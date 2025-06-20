from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from fastapi import WebSocket
import logging

logger = logging.getLogger("agent_manager")


class AgentInfo:
    """Runtime information for a connected agent."""

    def __init__(self, websocket: WebSocket, category: str, os_name: str, capabilities: Optional[str]):
        self.websocket = websocket
        self.category = category
        self.os = os_name
        self.capabilities = capabilities
        self.queue: asyncio.Queue[int] = asyncio.Queue()
        self.busy = False
        self.last_heartbeat = datetime.utcnow()
        self.start_time = datetime.utcnow()
        self.executions = 0
        self.successes = 0

    def touch(self) -> None:
        self.last_heartbeat = datetime.utcnow()

    def online(self) -> bool:
        return datetime.utcnow() - self.last_heartbeat < timedelta(seconds=60)

    @property
    def uptime(self) -> timedelta:
        return datetime.utcnow() - self.start_time

    @property
    def success_rate(self) -> float:
        return self.successes / self.executions if self.executions else 0.0


class AgentManager:
    """Manage execution agents connected via WebSocket."""

    def __init__(self) -> None:
        self.agents_by_category: Dict[str, List[AgentInfo]] = defaultdict(list)
        self.pending_by_category: Dict[str, asyncio.Queue[int]] = defaultdict(asyncio.Queue)
        self.lock = asyncio.Lock()
        self._health_task: Optional[asyncio.Task] = None

    async def register_agent(self, websocket: WebSocket, info: dict) -> AgentInfo:
        agent = AgentInfo(
            websocket=websocket,
            category=info.get("category", "web"),
            os_name=info.get("os", ""),
            capabilities=info.get("capabilities"),
        )
        async with self.lock:
            self.agents_by_category[agent.category].append(agent)
        logger.info("Agent connected: %s", info)
        return agent

    async def remove_agent(self, agent: AgentInfo) -> None:
        async with self.lock:
            if agent in self.agents_by_category.get(agent.category, []):
                self.agents_by_category[agent.category].remove(agent)
        logger.info("Agent removed: %s", agent.websocket.client)

    async def allocate_agent(self, category: str, os_name: Optional[str] = None) -> Optional[AgentInfo]:
        async with self.lock:
            for agent in self.agents_by_category.get(category, []):
                if agent.online() and not agent.busy and (os_name is None or agent.os == os_name):
                    agent.busy = True
                    return agent
        return None

    async def enqueue_pending(self, category: str, test_id: int) -> None:
        await self.pending_by_category[category].put(test_id)

    async def distribute_execution(self, test_id: int, name: str, description: str = "") -> Optional[AgentInfo]:
        category = self.detect_category(name, description)
        agent = await self.allocate_agent(category)
        if agent:
            await agent.queue.put(test_id)
            return agent
        await self.enqueue_pending(category, test_id)
        return None

    @staticmethod
    def detect_category(name: str, description: str) -> str:
        text = f"{name} {description}".lower()
        if "mobile" in text:
            return "mobile"
        if "api" in text:
            return "api"
        return "web"

    async def _dispatch_for_agent(self, agent: AgentInfo) -> None:
        if not agent.busy and not agent.queue.empty():
            test_id = await agent.queue.get()
            try:
                await agent.websocket.send_json({"type": "execute", "test_id": test_id})
            except Exception as exc:
                logger.error("Send execute failed: %s", exc)
                await self.enqueue_pending(agent.category, test_id)
                await self.remove_agent(agent)

    async def health_check_loop(self) -> None:
        while True:
            await asyncio.sleep(30)
            async with self.lock:
                cats = list(self.agents_by_category.items())
            for cat, agents in cats:
                for agent in list(agents):
                    if not agent.online():
                        await self.remove_agent(agent)
                        continue
                    try:
                        await agent.websocket.send_json({"type": "ping"})
                    except Exception:
                        await self.remove_agent(agent)
                        continue
                    await self._dispatch_for_agent(agent)
                # assign pending tasks if free agents
                while not self.pending_by_category[cat].empty():
                    agent = await self.allocate_agent(cat)
                    if not agent:
                        break
                    test_id = await self.pending_by_category[cat].get()
                    await agent.queue.put(test_id)
                    await self._dispatch_for_agent(agent)

    def start(self) -> None:
        if self._health_task is None:
            self._health_task = asyncio.create_task(self.health_check_loop())

    def get_metrics(self) -> list[dict]:
        """Return runtime statistics for all connected agents."""
        metrics = []
        for agents in self.agents_by_category.values():
            for agent in agents:
                metrics.append({
                    "category": agent.category,
                    "os": agent.os,
                    "busy": agent.busy,
                    "uptime": agent.uptime.total_seconds(),
                    "executions": agent.executions,
                    "success_rate": agent.success_rate,
                })
        return metrics


# Global manager instance
agent_manager = AgentManager()


async def allocate_agent(category: str, os_name: Optional[str] = None) -> Optional[AgentInfo]:
    """Public helper to allocate an available agent."""
    return await agent_manager.allocate_agent(category, os_name)

