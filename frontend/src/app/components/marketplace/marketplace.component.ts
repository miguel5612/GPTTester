import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarketplaceComponent as Item } from '../../models';
import { MarketplaceService } from '../../services/marketplace.service';
import { ComponentFormComponent } from './component-form.component';

@Component({
  selector: 'app-marketplace',
  standalone: true,
  imports: [CommonModule, FormsModule, ComponentFormComponent],
  template: `
    <div class="main-panel">
      <h1>Marketplace</h1>
      <div class="mb-3">
        <button class="btn btn-primary" (click)="new()">Nuevo</button>
      </div>
      <table class="table table-bordered" *ngIf="components.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Versión</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let c of components">
            <td>{{ c.name }}</td>
            <td>{{ c.version }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(c)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(c)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="components.length === 0">No hay componentes.</div>

      <app-component-form *ngIf="showForm" [component]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-component-form>
    </div>
  `,
  styles: [`
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class MarketplaceComponent implements OnInit {
  components: Item[] = [];
  showForm = false;
  editing: Item | null = null;

  constructor(private service: MarketplaceService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getComponents().subscribe(c => this.components = c);
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(c: Item) {
    this.editing = c;
    this.showForm = true;
  }

  remove(c: Item) {
    if (confirm('¿Eliminar componente?')) {
      this.service.deleteComponent(c.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
