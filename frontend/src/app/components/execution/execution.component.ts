import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-execution',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Centro de Ejecución</h1>
      <p class="text-secondary">Monitorea y controla las ejecuciones de pruebas</p>
      
      <div class="section">
        <h2>Próximamente</h2>
        <p>Esta funcionalidad estará disponible próximamente.</p>
      </div>
    </div>
  `
})
export class ExecutionComponent {}
