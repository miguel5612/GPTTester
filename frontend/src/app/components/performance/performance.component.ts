import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PerformanceService } from '../../services/performance.service';

@Component({
  selector: 'app-performance',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Motor de Performance</h1>
      <p class="text-secondary">Descarga el script de carga generado a partir de los tests funcionales.</p>
      <button class="btn btn-primary" (click)="download()">Descargar Script K6</button>
    </div>
  `,
  styles: []
})
export class PerformanceComponent {
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
}
