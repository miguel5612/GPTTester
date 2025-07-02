import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PerformanceService } from '../../services/performance.service';
import { PerformanceScenarioSelectorComponent } from './performance-scenario-selector.component';
import { PerformanceConfigFormComponent, PerformanceConfig } from './performance-config-form.component';
import { PerformanceResultsComponent } from './performance-results.component';
import { Scenario } from '../../models';

@Component({
  selector: 'app-performance',
  standalone: true,
  imports: [
    CommonModule,
    PerformanceScenarioSelectorComponent,
    PerformanceConfigFormComponent,
    PerformanceResultsComponent
  ],
  template: `
    <div class="main-panel">
      <h1>Motor de Performance</h1>
      <p class="text-secondary">Descarga el script de carga generado a partir de los tests funcionales.</p>
      <button class="btn btn-primary mb-3" (click)="download()">Descargar Script K6</button>

      <app-performance-scenario-selector (selected)="onSelectScenario($event)"></app-performance-scenario-selector>

      <app-performance-config-form (run)="runTest($event)" *ngIf="selectedScenario"></app-performance-config-form>

      <app-performance-results [results]="results"></app-performance-results>
    </div>
  `,
  styles: []
})
export class PerformanceComponent {
  selectedScenario: Scenario | null = null;
  results: any;

  constructor(private service: PerformanceService) {}

  download() {
    this.service.downloadK6Script().subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'script.js';
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  onSelectScenario(s: Scenario | null) {
    this.selectedScenario = s;
    this.results = null;
  }

  runTest(cfg: PerformanceConfig) {
    if (!this.selectedScenario) {
      return;
    }
    this.service.startTest(this.selectedScenario.id, cfg).subscribe(r => {
      this.results = r;
    });
  }
}
