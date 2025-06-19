import { Component, Input, OnInit, OnDestroy, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonitorService } from '../../services/monitor.service';
import { PlanExecution } from '../../models';

@Component({
  selector: 'app-execution-monitor',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="monitor">
      <div class="d-flex justify-content-between align-items-center mb-1">
        <strong>Ejecución {{execution.id}}</strong>
        <span class="badge bg-info">{{ status }}</span>
      </div>
      <div class="progress mb-1">
        <div class="progress-bar" role="progressbar" [style.width.%]="progress"></div>
      </div>
      <pre class="logs" #logBox>{{ logText }}</pre>
      <img *ngIf="screenshot" [src]="screenshot" class="img-fluid mb-2" />
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-secondary" (click)="pause()" *ngIf="status==='En ejecucion'">Pausar</button>
        <button class="btn btn-sm btn-secondary" (click)="resume()" *ngIf="status==='Pausado'">Reanudar</button>
        <button class="btn btn-sm btn-danger" (click)="cancel()">Cancelar</button>
        <button class="btn btn-sm btn-link" (click)="close.emit(execution)">Cerrar</button>
      </div>
    </div>
  `,
  styles: [`
    .monitor { border:1px solid #ddd; padding:0.5rem; border-radius:4px; background:#fff; }
    .logs { height:100px; overflow:auto; background:#f7f7f7; padding:0.25rem; }
  `]
})
export class ExecutionMonitorComponent implements OnInit, OnDestroy {
  @Input() execution!: PlanExecution;
  @Output() close = new EventEmitter<PlanExecution>();

  status = '';
  progress = 0;
  logs: string[] = [];
  screenshot: string | null = null;
  private socket: any;

  constructor(private monitor: MonitorService) {}

  ngOnInit() {
    this.status = this.execution.status;
    this.socket = this.monitor.connect(this.execution.id);
    this.socket.subscribe((msg: any) => {
      if (msg.status) this.status = msg.status;
      if (msg.progress !== undefined) this.progress = msg.progress;
      if (msg.log) {
        this.logs.push(msg.log);
        setTimeout(() => {
          const box = document.querySelector('.logs');
          if (box) box.scrollTop = box.scrollHeight;
        });
      }
      if (msg.screenshot) this.screenshot = msg.screenshot;
    });
  }

  ngOnDestroy() {
    if (this.socket) this.socket.complete();
  }

  get logText() { return this.logs.join('\n'); }

  pause() { this.monitor.pause(this.execution.id).subscribe(); }
  resume() { this.monitor.resume(this.execution.id).subscribe(); }
  cancel() { if (confirm('Cancelar ejecución?')) this.monitor.cancel(this.execution.id).subscribe(); }
}
