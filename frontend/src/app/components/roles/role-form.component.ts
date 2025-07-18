import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Role, RoleCreate } from '../../models';
import { RoleService } from '../../services/role.service';

@Component({
  selector: 'app-role-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-body">
        <h3 class="card-title">{{ role ? 'Editar Rol' : 'Nuevo Rol' }}</h3>
        <form (ngSubmit)="save()">
          <div class="mb-3">
            <label class="form-label">Nombre</label>
            <input class="form-control" [(ngModel)]="form.name" name="name" required>
          </div>
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="active" [(ngModel)]="form.is_active" name="is_active">
            <label class="form-check-label" for="active">Activo</label>
          </div>
          <button class="btn btn-primary" type="submit">Guardar</button>
          <button type="button" class="btn btn-secondary ms-2" (click)="cancel.emit()">Cancelar</button>
        </form>
      </div>
    </div>
  `
})
export class RoleFormComponent {
  @Input() role: Role | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: RoleCreate = { name: '', is_active: true };

  constructor(private service: RoleService) {}

  ngOnInit() {
    if (this.role) {
      this.form = { name: this.role.name, is_active: this.role.is_active };
    }
  }

  save() {
    const obs = this.role
      ? this.service.updateRole(this.role.id, this.form)
      : this.service.createRole(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
