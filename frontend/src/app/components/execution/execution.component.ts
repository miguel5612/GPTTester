import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExecutionService } from '../../services/execution.service';
import { ExecutionPlan, PlanExecution } from '../../models';

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
        <button class="btn btn-primary" (click)="run()" [disabled]="!planId">Ejecutar</button>
        <button class="btn btn-secondary" (click)="loadExecutions()">Refrescar</button>
      </div>

      <table class="table table-bordered" *ngIf="executions.length > 0">
        <thead>
          <tr>
            <th>Plan</th>
            <th>Agente</th>
            <th>Estado</th>
            <th>Inicio</th>
            <th>Descargas</th>
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
          </tr>
        </tbody>
      </table>
      <div *ngIf="executions.length === 0" class="mt-3">No hay ejecuciones.</div>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class ExecutionComponent implements OnInit, OnDestroy {
  plans: ExecutionPlan[] = [];
  executions: ExecutionView[] = [];
  planId: number | null = null;
  private interval: any;

  constructor(private service: ExecutionService) {}

  ngOnInit() {
    this.loadPlans();
    this.loadExecutions();
    this.interval = setInterval(() => this.loadExecutions(), 5000);
  }

  ngOnDestroy() {
    if (this.interval) {
      clearInterval(this.interval);
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

  planName(id: number): string {
    const p = this.plans.find(pl => pl.id === id);
    return p ? p.nombre : `${id}`;
  }

  run() {
    if (!this.planId) return;
    this.service.runPlan(this.planId).subscribe(() => this.loadExecutions());
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
