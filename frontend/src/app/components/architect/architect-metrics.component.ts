import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-architect-metrics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Métricas de Arquitecto</h1>
      <div *ngIf="metrics">
        <p><strong>Scripts por día:</strong> {{ metrics.scripts_per_day }}</p>
        <p><strong>Proyectos activos:</strong> {{ metrics.active_projects }}</p>
        <p><strong>Interacciones pendientes:</strong> {{ metrics.pending_interactions }}</p>
        <p><strong>Validaciones pendientes:</strong> {{ metrics.pending_validations }}</p>
      </div>
    </div>
  `
})
export class ArchitectMetricsComponent implements OnInit {
  metrics: any;
  constructor(private api: ApiService) {}

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    // Metrics are fetched from backend and kept up to date
    this.api.getDashboardMetrics().subscribe(m => (this.metrics = m));
  }
}
