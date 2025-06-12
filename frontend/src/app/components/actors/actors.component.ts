import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-actors',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Gestión de Actores</h1>
      <p class="text-secondary">Administra los actores del sistema de automatización</p>
      
      <div class="section">
        <h2>Próximamente</h2>
        <p>Esta funcionalidad estará disponible próximamente.</p>
      </div>
    </div>
  `
})
export class ActorsComponent {}
