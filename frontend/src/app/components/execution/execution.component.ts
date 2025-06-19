import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExecutionService } from '../../services/execution.service';
import { AgentService } from '../../services/agent.service';
import { ExecutionPlan, PlanExecution, Agent, ExecutionLog, ExecutionSchedule, ExecutionScheduleCreate } from '../../models';

interface ExecutionView extends PlanExecution {
  planName?: string;
}

@Component({
  selector: 'app-execution',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Centro de Ejecución</h1>
      <p class="text-secondary">Monitorea y controla las ejecuciones de pruebas</p>

      <div class="mb-3 d-flex flex-wrap gap-2 align-items-end">
        <select class="form-control" [(ngModel)]="planId">
          <option [ngValue]="null">Seleccionar plan</option>
          <option *ngFor="let p of plans" [ngValue]="p.id">{{ p.nombre }}</option>
        </select>
        <select class="form-control" [(ngModel)]="selectedAgentId">
          <option [ngValue]="null">Auto-asignar</option>
          <option *ngFor="let a of agents" [ngValue]="a.id">{{ a.alias }}</option>
        </select>
        <button class="btn btn-primary" (click)="run()" [disabled]="!planId">Ejecutar Ahora</button>
        <button class="btn btn-secondary" (click)="loadExecutions()">Refrescar</button>
      </div>

      <div class="mb-4">
        <h3>Programar Ejecución</h3>
        <div class="d-flex flex-wrap gap-2 align-items-end">
          <select class="form-control" [(ngModel)]="schedulePlanId">
            <option [ngValue]="null">Plan</option>
            <option *ngFor="let p of plans" [ngValue]="p.id">{{ p.nombre }}</option>
          </select>
          <select class="form-control" [(ngModel)]="scheduleAgentId">
            <option [ngValue]="null">Auto-asignar</option>
            <option *ngFor="let a of agents" [ngValue]="a.id">{{ a.alias }}</option>
          </select>
          <input type="datetime-local" class="form-control" [(ngModel)]="scheduleTime">
          <button class="btn btn-outline-primary" (click)="schedule()">Programar</button>
        </div>
      </div>

      <table class="table table-bordered" *ngIf="executions.length > 0">
        <thead>
          <tr>
            <th>Plan</th>
            <th>Agente</th>
            <th>Estado</th>
            <th>Inicio</th>
            <th>Descargas</th>
            <th>Monitor</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let e of executions">
            <td>{{ e.planName || e.plan_id }}</td>
            <td>{{ e.agent_id }}</td>
            <td>{{ e.status }}</td>
            <td>{{ e.started_at | date:'short' }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary mr-2" (click)="download(e, 'report')" [disabled]="e.status !== 'Finalizado'">PDF</button>
              <button class="btn btn-sm btn-outline-secondary" (click)="download(e, 'evidence')" [disabled]="e.status !== 'Finalizado'">ZIP</button>
            </td>
            <td><button class="btn btn-sm btn-info" (click)="viewExecution(e)">Ver</button></td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="executions.length === 0" class="mt-3">No hay ejecuciones.</div>

      <div *ngIf="selectedExecution" class="mt-4">
        <h3>Monitoreo</h3>
        <p>Estado: {{ selectedExecution?.status }}</p>
        <p>Tiempo transcurrido: {{ elapsed }} s</p>
        <pre class="logs">{{ logText }}</pre>
      </div>

      <div class="mt-4" *ngIf="schedules.length > 0">
        <h3>Próximas Ejecuciones</h3>
        <table class="table table-bordered">
          <thead>
            <tr><th>Plan</th><th>Agente</th><th>Fecha</th><th></th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let s of schedules">
              <td>{{ planName(s.plan_id) }}</td>
              <td>{{ s.agent_id || 'Auto' }}</td>
              <td>{{ s.run_at | date:'short' }}</td>
              <td><button class="btn btn-sm btn-danger" (click)="removeSchedule(s)">X</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
    .logs { background:#f1f1f1; padding:0.5rem; max-height:200px; overflow:auto; }
  `]
})
export class ExecutionComponent implements OnInit, OnDestroy {
  plans: ExecutionPlan[] = [];
  executions: ExecutionView[] = [];
  schedules: ExecutionSchedule[] = [];
  planId: number | null = null;
  selectedAgentId: number | null = null;
  private interval: any;
  private logInterval: any;
  selectedExecution: PlanExecution | null = null;
  logs: ExecutionLog[] = [];
  elapsed = 0;

  schedulePlanId: number | null = null;
  scheduleAgentId: number | null = null;
  scheduleTime = '';
  agents: Agent[] = [];

  constructor(private service: ExecutionService, private agentService: AgentService) {}

  ngOnInit() {
    this.loadPlans();
    this.loadExecutions();
    this.loadAgents();
    this.loadSchedules();
    this.interval = setInterval(() => this.loadExecutions(), 5000);
  }

  ngOnDestroy() {
    if (this.interval) {
      clearInterval(this.interval);
    }
    if (this.logInterval) {
      clearInterval(this.logInterval);
    }
  }

  loadPlans() {
    this.service.getPlans().subscribe(p => this.plans = p);
  }

  loadExecutions() {
    this.service.getExecutions().subscribe(list => {
      this.executions = list.map(e => ({ ...e, planName: this.planName(e.plan_id) }));
    });
  }

  loadAgents() {
    this.agentService.getAgents().subscribe(a => this.agents = a);
  }

  loadSchedules() {
    this.service.getSchedules().subscribe(s => this.schedules = s.filter(sc => !sc.executed));
  }

  planName(id: number): string {
    const p = this.plans.find(pl => pl.id === id);
    return p ? p.nombre : `${id}`;
  }

  run() {
    if (!this.planId) return;
    this.service.runPlan(this.planId, this.selectedAgentId ?? undefined).subscribe(e => {
      this.loadExecutions();
      this.viewExecution(e);
    });
  }

  schedule() {
    if (!this.schedulePlanId || !this.scheduleTime) return;
    const payload: ExecutionScheduleCreate = {
      plan_id: this.schedulePlanId,
      run_at: this.scheduleTime,
      agent_id: this.scheduleAgentId || undefined
    };
    this.service.createSchedule(payload).subscribe(() => this.loadSchedules());
  }

  removeSchedule(s: ExecutionSchedule) {
    this.service.deleteSchedule(s.id).subscribe(() => this.loadSchedules());
  }

  viewExecution(exec: PlanExecution) {
    this.selectedExecution = exec;
    this.fetchLogs();
    this.updateElapsed();
    if (this.logInterval) clearInterval(this.logInterval);
    this.logInterval = setInterval(() => {
      this.service.getExecution(exec.id).subscribe(r => this.selectedExecution = r);
      this.fetchLogs();
      this.updateElapsed();
    }, 3000);
  }

  fetchLogs() {
    if (!this.selectedExecution) return;
    this.service.getExecutionLogs(this.selectedExecution.id).subscribe(l => {
      this.logs = l;
    });
  }

  get logText(): string {
    return this.logs.map(l => l.message).join('\n');
  }

  updateElapsed() {
    if (this.selectedExecution) {
      this.elapsed = Math.floor((Date.now() - new Date(this.selectedExecution.started_at).getTime()) / 1000);
    }
  }

  download(exec: PlanExecution, type: 'report' | 'evidence') {
    this.service.downloadReport(exec.id, type).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exec.id}-${type}.` + (type === 'report' ? 'pdf' : 'zip');
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}
