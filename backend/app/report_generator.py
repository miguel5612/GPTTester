import io
import json
import os
import zipfile
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
from weasyprint import HTML

from . import models


def _load_template(client_id: int | None = None) -> Environment:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    if client_id:
        custom = os.path.join(base_dir, str(client_id))
        if os.path.isdir(custom):
            return Environment(loader=FileSystemLoader(custom))
    default = os.path.join(base_dir, "default")
    return Environment(loader=FileSystemLoader(default))


class ReportGenerator:
    """Generate PDF execution reports using HTML templates."""

    def __init__(self, client_id: int | None = None) -> None:
        self.env = _load_template(client_id)
        self.template = self.env.get_template("report.html")

    def render(self, context: Dict[str, Any]) -> bytes:
        html = self.template.render(**context)
        return HTML(string=html, base_url="/").write_pdf()


def _extract_result_zip(execution_id: int, target_dir: str) -> None:
    path = os.path.join("/tmp", f"result_{execution_id}.zip")
    if not os.path.exists(path):
        return
    with zipfile.ZipFile(path) as z:
        z.extractall(target_dir)


def _generate_step_chart(logs: List[models.ExecutionLog], output: str) -> None:
    if not logs:
        return
    timestamps = [log.timestamp for log in logs]
    start = min(timestamps)
    steps = [ts - start for ts in timestamps]
    seconds = [s.total_seconds() for s in steps]
    plt.figure(figsize=(6, 2))
    plt.plot(seconds, list(range(1, len(seconds) + 1)), marker="o")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Paso")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def generate_execution_report(db: Session, execution_id: int) -> str:
    record = db.query(models.PlanExecution).filter(models.PlanExecution.id == execution_id).first()
    if not record:
        raise ValueError("Execution not found")
    client_id = record.plan.test.owner.clients[0].id if record.plan.test.owner.clients else None
    generator = ReportGenerator(client_id)

    logs = db.query(models.ExecutionLog).filter(models.ExecutionLog.execution_id == execution_id).order_by(models.ExecutionLog.timestamp).all()
    workdir = os.path.join("/tmp", f"exec_{execution_id}")
    os.makedirs(workdir, exist_ok=True)
    _extract_result_zip(execution_id, workdir)
    chart_path = os.path.join(workdir, "steps.png")
    _generate_step_chart(logs, chart_path)

    summary_html = f"<p>Status: {record.status}</p><p>Agente: {record.agent.alias}</p>"
    detail_rows = [f"<li>{log.timestamp} - {log.message}</li>" for log in logs]
    detail_html = f"<ul>{''.join(detail_rows)}</ul><img src='{chart_path}' width='500'>"
    evidence_parts = []
    shots_dir = os.path.join(workdir, "screenshots")
    if os.path.isdir(shots_dir):
        for fname in sorted(os.listdir(shots_dir)):
            fpath = os.path.join(shots_dir, fname)
            evidence_parts.append(f"<div><img src='{fpath}' width='500'><p>{fname}</p></div>")
    evidence_html = "".join(evidence_parts)

    default_logo = os.path.join(
        os.path.dirname(__file__), "..", "templates", "default", "logo.png"
    )
    logo_path = default_logo if os.path.exists(default_logo) else None
    pdf_bytes = generator.render(
        {
            "execution": record,
            "summary": summary_html,
            "detail": detail_html,
            "evidence": evidence_html,
            "generated_at": datetime.utcnow().isoformat(),
            "watermark": record.plan.nombre,
            "logo": logo_path,
        }
    )
    pdf_path = os.path.join("/tmp", f"report_{execution_id}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    return pdf_path


def package_evidence(db: Session, execution_id: int) -> str:
    record = db.query(models.PlanExecution).filter(models.PlanExecution.id == execution_id).first()
    if not record:
        raise ValueError("Execution not found")

    report_path = os.path.join("/tmp", f"report_{execution_id}.pdf")
    if not os.path.exists(report_path):
        generate_execution_report(db, execution_id)

    workdir = os.path.join("/tmp", f"exec_{execution_id}")
    os.makedirs(workdir, exist_ok=True)
    _extract_result_zip(execution_id, workdir)

    data_dir = os.path.join(workdir, "data")
    os.makedirs(data_dir, exist_ok=True)

    logs = db.query(models.ExecutionLog).filter(models.ExecutionLog.execution_id == execution_id).order_by(models.ExecutionLog.timestamp).all()
    log_dir = os.path.join(workdir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "logs.txt"), "w") as f:
        for log in logs:
            f.write(f"{log.timestamp.isoformat()} - {log.message}\n")

    stats = {
        "status": record.status,
        "total_logs": len(logs),
    }
    with open(os.path.join(data_dir, "stats.json"), "w") as f:
        json.dump(stats, f)

    zip_path = os.path.join("/tmp", f"evidence_{execution_id}.zip")
    with zipfile.ZipFile(zip_path, "w") as z:
        for folder in ["screenshots", "logs", "data"]:
            folder_path = os.path.join(workdir, folder)
            if not os.path.isdir(folder_path):
                continue
            for root_dir, _, files in os.walk(folder_path):
                for file in files:
                    full = os.path.join(root_dir, file)
                    arc = os.path.relpath(full, workdir)
                    z.write(full, arc)
        z.write(report_path, "report.pdf")
    return zip_path
