import { Component, EventEmitter, Input, Output, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarketplaceComponent, MarketplaceComponentCreate } from '../../models';
import { MarketplaceService } from '../../services/marketplace.service';

@Component({
  selector: 'app-component-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="component-form">
      <h2>{{ component ? 'Editar' : 'Crear' }} Componente</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="form-group">
          <label>Descripción</label>
          <textarea class="form-control" [(ngModel)]="form.description" name="description"></textarea>
        </div>
        <div class="form-group">
          <label>Versión</label>
          <input class="form-control" [(ngModel)]="form.version" name="version">
        </div>
        <div class="form-group">
          <label>Código</label>
          <textarea class="form-control" [(ngModel)]="form.code" name="code" rows="5" required></textarea>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .component-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class ComponentFormComponent implements OnChanges {
  @Input() component: MarketplaceComponent | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: MarketplaceComponentCreate = { name: '', description: '', code: '', version: '0.1.0' };

  constructor(private service: MarketplaceService) {}

  ngOnChanges() {
    if (this.component) {
      this.form = { name: this.component.name, description: this.component.description, code: this.component.code, version: this.component.version };
    } else {
      this.form = { name: '', description: '', code: '', version: '0.1.0' };
    }
  }

  submit() {
    const obs = this.component ?
      this.service.updateComponent(this.component.id, this.form) :
      this.service.createComponent(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
