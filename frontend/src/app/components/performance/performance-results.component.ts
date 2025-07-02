import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-performance-results',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="results; else empty">
      <h3>Resultados</h3>
      <pre>{{ results | json }}</pre>
    </div>
    <ng-template #empty>
      <p class="text-secondary">No hay resultados</p>
    </ng-template>
  `
})
export class PerformanceResultsComponent {
  @Input() results: any;
}
