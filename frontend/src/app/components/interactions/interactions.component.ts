import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-interactions',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Interacciones por Defecto</h1>
    </div>
  `
})
export class InteractionsComponent {}
