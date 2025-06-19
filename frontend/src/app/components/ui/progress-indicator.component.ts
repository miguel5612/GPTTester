import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-progress-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="progress-indicator">
      <div class="step" *ngFor="let s of steps; let i = index" [class.active]="i <= current">
        <span class="circle">{{ i + 1 }}</span>
        <span class="label">{{ s }}</span>
      </div>
    </div>
  `,
  styles: [`
    :host { display:block; container-type:inline-size; }
    .progress-indicator { display:flex; flex-direction:column; gap:0.5rem; }
    .step { display:flex; align-items:center; gap:0.5rem; color:var(--secondary-text); }
    .circle { width:1.5rem; height:1.5rem; border-radius:50%; background:var(--checkbox-color); color:var(--panel-bg); display:flex; align-items:center; justify-content:center; font-size:0.8rem; }
    .step.active .circle { background:var(--btn-primary); }
    .step.active { color:var(--title-color); }
    @container (min-width:768px) { .progress-indicator { flex-direction:row; } }
  `]
})
export class ProgressIndicatorComponent {
  @Input() steps: string[] = [];
  @Input() current = 0;
}
