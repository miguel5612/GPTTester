import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Role } from '../../models';
import { RoleService } from '../../services/role.service';
import { RoleFormComponent } from './role-form.component';

@Component({
  selector: 'app-roles',
  standalone: true,
  imports: [CommonModule, FormsModule, RoleFormComponent],
  template: `
    <div class="main-panel">
      <h1>Roles</h1>
      <button class="btn btn-primary mb-2" (click)="new()">Nuevo Rol</button>
      <table class="table" *ngIf="roles.length > 0">
        <thead>
          <tr><th>Nombre</th><th></th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let r of roles">
            <td>{{ r.name }}</td>
            <td>
              <button class="btn btn-sm btn-secondary me-2" (click)="edit(r)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(r)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="roles.length === 0">No hay roles.</div>

      <app-role-form *ngIf="showForm" [role]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-role-form>
    </div>
  `
})
export class RolesComponent implements OnInit {
  roles: Role[] = [];
  showForm = false;
  editing: Role | null = null;

  constructor(private service: RoleService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getRoles().subscribe(list => this.roles = list);
  }

  new() { this.editing = null; this.showForm = true; }

  edit(r: Role) { this.editing = r; this.showForm = true; }

  remove(r: Role) {
    if (confirm('¿Eliminar rol?')) {
      this.service.deleteRole(r.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
