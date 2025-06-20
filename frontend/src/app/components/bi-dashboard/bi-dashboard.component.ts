import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { NgChartsModule } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import jsPDF from 'jspdf';

@Component({
  selector: 'app-bi-dashboard',
  standalone: true,
  imports: [CommonModule, NgChartsModule],
  template: `
    <div class="main-panel">
      <h1>BI Dashboard</h1>
      <button class="btn btn-primary mb-3" (click)="exportPdf()">Exportar PDF</button>
      <div *ngIf="metrics?.manager">
        <h2>Scripts por Cliente</h2>
        <canvas baseChart [data]="clientChartData" [type]="'pie'"></canvas>

        <h2 class="mt-4">Scripts por Analista</h2>
        <canvas baseChart [data]="analystChartData" [type]="'pie'"></canvas>

        <div class="mt-4">
          <p><strong>Mejor analista:</strong> {{ metrics.manager.best_analyst || 'N/A' }}</p>
          <p><strong>Ejecuciones fallidas:</strong> {{ metrics.manager.failed_executions || 0 }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .main-panel { padding: 1rem; }
    canvas { max-width: 400px; display: block; margin: 1rem auto; }
  `]
})
export class BiDashboardComponent implements OnInit {
  metrics: any;
  clientChartData: ChartConfiguration<'pie'>['data'] = { labels: [], datasets: [{ data: [] }] };
  analystChartData: ChartConfiguration<'pie'>['data'] = { labels: [], datasets: [{ data: [] }] };

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getDashboardMetrics().subscribe(m => {
      this.metrics = m;
      this.prepareCharts();
    });
  }

  prepareCharts() {
    if (!this.metrics?.manager) return;
    const clients = this.metrics.manager.clients || [];
    this.clientChartData.labels = clients.map((c: any) => c.name);
    this.clientChartData.datasets[0].data = clients.map((c: any) => c.scripts);

    const analysts = this.metrics.manager.analysts || [];
    this.analystChartData.labels = analysts.map((a: any) => a.name);
    this.analystChartData.datasets[0].data = analysts.map((a: any) => a.scripts);
  }

  exportPdf() {
    const doc = new jsPDF();
    doc.text('BI Dashboard Metrics', 10, 10);
    doc.text(JSON.stringify(this.metrics, null, 2), 10, 20);
    doc.save('bi-dashboard.pdf');
  }
}
