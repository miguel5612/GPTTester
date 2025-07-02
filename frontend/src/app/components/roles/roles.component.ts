import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Role } from '../../models';
import { RoleService } from '../../services/role.service';
import { RoleFormComponent } from './role-form.component';
import { RolePermissionsComponent } from './role-permissions.component';

@Component({
  selector: 'app-roles',
  standalone: true,
  imports: [CommonModule, FormsModule, RoleFormComponent, RolePermissionsComponent],
  template: `
    <div class="main-panel">
      <h1>Roles</h1>
      <button class="btn btn-primary mb-2" (click)="new()">Nuevo Rol</button>
      <table class="table" *ngIf="roles.length > 0">
        <thead>
          <tr><th>Nombre</th><th>Activo</th><th></th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let r of roles">
            <td>{{ r.name }}</td>
            <td>
              <input class="form-check-input" type="checkbox" [checked]="r.is_active" (change)="toggleActive(r, $any($event.target).checked)">
            </td>
            <td>
              <button class="btn btn-sm btn-secondary me-2" (click)="edit(r)">Editar</button>
              <button class="btn btn-sm btn-info me-2" (click)="permissions(r)">Permisos</button>
              <button class="btn btn-sm btn-danger" (click)="remove(r)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="roles.length === 0">No hay roles.</div>

      <app-role-form *ngIf="showForm" [role]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-role-form>
      <app-role-permissions *ngIf="selectedRole" [role]="selectedRole" (close)="selectedRole=null"></app-role-permissions>
    </div>
  `
})
export class RolesComponent implements OnInit {
  roles: Role[] = [];
  showForm = false;
  editing: Role | null = null;
  selectedRole: Role | null = null;

  constructor(private service: RoleService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getRoles().subscribe(list => this.roles = list);
  }

  new() { this.editing = null; this.showForm = true; }

  edit(r: Role) { this.editing = r; this.showForm = true; }

  permissions(r: Role) { this.selectedRole = r; }

  remove(r: Role) {
    if (confirm('¿Eliminar rol?')) {
      this.service.deleteRole(r.id).subscribe(() => this.load());
    }
  }

  toggleActive(role: Role, active: boolean) {
    this.service.updateRoleActive(role.id, active).subscribe(r => role.is_active = r.is_active);
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
