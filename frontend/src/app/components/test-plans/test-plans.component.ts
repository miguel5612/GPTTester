import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-test-plans',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Planes de Prueba</h1>
      <p class="text-secondary">Gestiona los planes de prueba del sistema</p>
      
      <div class="section">
        <h2>Próximamente</h2>
        <p>Esta funcionalidad estará disponible próximamente.</p>
      </div>
    </div>
  `
})
export class TestPlansComponent {}
