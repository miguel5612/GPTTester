import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface PerformanceConfig {
  vus: number;
  rampUp: number;
  duration: number;
}

@Component({
  selector: 'app-performance-config-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <form (ngSubmit)="submit()" #form="ngForm" class="mb-3">
      <div class="row g-2">
        <div class="col">
          <input type="number" class="form-control" name="vus" [(ngModel)]="config.vus" required min="1" placeholder="Usuarios">
        </div>
        <div class="col">
          <input type="number" class="form-control" name="ramp" [(ngModel)]="config.rampUp" required min="0" placeholder="Ramp-up (s)">
        </div>
        <div class="col">
          <input type="number" class="form-control" name="dur" [(ngModel)]="config.duration" required min="1" placeholder="Duración (s)">
        </div>
        <div class="col-auto">
          <button class="btn btn-success" [disabled]="form.invalid">Ejecutar</button>
        </div>
      </div>
    </form>
  `
})
export class PerformanceConfigFormComponent {
  @Input() config: PerformanceConfig = { vus: 1, rampUp: 0, duration: 60 };
  @Output() run = new EventEmitter<PerformanceConfig>();

  submit() {
    this.run.emit(this.config);
  }
}
