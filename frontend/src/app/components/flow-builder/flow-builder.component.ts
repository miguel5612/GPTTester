import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-flow-builder',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Constructor de Flujos</h1>
      <p class="text-secondary">Crea y edita flujos de automatización</p>
      
      <div class="section">
        <h2>Próximamente</h2>
        <p>Esta funcionalidad estará disponible próximamente.</p>
      </div>
    </div>
  `
})
export class FlowBuilderComponent {}
