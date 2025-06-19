import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExecutionService } from '../../services/execution.service';
import { PlanExecution } from '../../models';
import { ExecutionMonitorComponent } from './execution-monitor.component';

@Component({
  selector: 'app-execution-monitor-page',
  standalone: true,
  imports: [CommonModule, ExecutionMonitorComponent],
  template: `
    <div class="main-panel">
      <h1>Monitoreo en Tiempo Real</h1>
      <div class="monitor-grid">
        <app-execution-monitor *ngFor="let e of monitors" [execution]="e" (close)="close(e)"></app-execution-monitor>
      </div>
    </div>
  `,
  styles: [`
    .monitor-grid { display:grid; gap:1rem; }
    @media (max-width: 767px) { .monitor-grid { grid-template-columns: 1fr; } }
    @media (min-width:768px) and (max-width:1023px) { .monitor-grid { grid-template-columns: repeat(2,1fr); } }
    @media (min-width:1024px) { .monitor-grid { grid-template-columns: repeat(4,1fr); } }
  `]
})
export class ExecutionMonitorPageComponent implements OnInit {
  monitors: PlanExecution[] = [];

  constructor(private execService: ExecutionService) {}

  ngOnInit() {
    this.load();
    setInterval(() => this.load(), 5000);
  }

  load() {
    this.execService.getExecutions().subscribe(list => {
      this.monitors = list.filter(e => e.status !== 'Finalizado');
    });
  }

  close(e: PlanExecution) {
    this.monitors = this.monitors.filter(m => m.id !== e.id);
  }
}
