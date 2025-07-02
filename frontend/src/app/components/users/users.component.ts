import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { UserFormComponent } from './user-form.component';
import { User, Role } from '../../models';
import { UserService } from '../../services/user.service';
import { RoleService } from '../../services/role.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, UserFormComponent],
  template: `
    <div class="main-panel">
      <h1>Usuarios</h1>
      <button class="btn btn-primary mb-2" (click)="new()">Nuevo Usuario</button>
      <table class="table" *ngIf="users.length > 0">
        <thead>
          <tr><th>Usuario</th><th>Rol</th><th>Último Login</th><th>Activo</th><th></th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let u of users">
            <td>{{ u.username }}</td>
            <td>
              <select class="form-select" [(ngModel)]="u.role.id" (change)="changeRole(u)">
                <option *ngFor="let r of roles" [ngValue]="r.id">{{ r.name }}</option>
              </select>
            </td>
            <td>{{ u.last_login ? (u.last_login | date:'short') : '-' }}</td>
            <td>
              <input type="checkbox"
                     [checked]="u.is_active"
                     (change)="toggleActive(u, $event)"
                     [disabled]="u.id === currentUserId" />
            </td>
            <td>
              <button class="btn btn-sm btn-secondary me-2" (click)="edit(u)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(u)" [disabled]="u.id === currentUserId">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="users.length === 0">No hay usuarios.</div>

      <app-user-form *ngIf="showForm" [user]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-user-form>

      <div *ngIf="message" class="alert alert-info mt-2">{{ message }}</div>
      <div *ngIf="error" class="alert alert-danger mt-2">{{ error }}</div>
    </div>
  `
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  roles: Role[] = [];
  currentUser: User | null = null;
  showForm = false;
  editing: User | null = null;
  message = '';
  error = '';

  constructor(
    private userService: UserService,
    private roleService: RoleService,
    private apiService: ApiService
  ) {}

  ngOnInit() {
    this.load();
    if (this.apiService.isAuthenticated()) {
      this.apiService.getCurrentUser().subscribe(u => this.currentUser = u);
    }
  }

  load() {
    this.roleService.getRoles().subscribe(rs => this.roles = rs);
    this.userService.getUsers().subscribe(us => this.users = us);
  }

  new() { this.editing = null; this.showForm = true; }

  edit(u: User) { this.editing = u; this.showForm = true; }

  remove(u: User) {
    if (confirm('¿Eliminar usuario?')) {
      this.userService.deleteUser(u.id).subscribe({
        next: () => { this.message = 'Usuario eliminado'; this.load(); },
        error: err => { this.error = err.error?.detail || 'Error al eliminar'; }
      });
    }
  }

  changeRole(user: User) {
    this.userService.updateUserRole(user.id, { role_id: user.role.id }).subscribe({
      next: () => this.message = 'Rol actualizado',
      error: err => this.error = err.error?.detail || 'Error al actualizar rol'
    });
  }

  toggleActive(user: User, event?: Event) {
    const checked = event ? (event.target as HTMLInputElement).checked : !user.is_active;
    this.userService.updateUserActive(user.id, checked)
      .subscribe({
        next: u => { user.is_active = u.is_active; this.message = 'Estado actualizado'; },
        error: err => this.error = err.error?.detail || 'Error al actualizar estado'
      });
  }

  onSaved() {
    this.showForm = false;
    this.load();
    this.message = this.editing ? 'Usuario actualizado' : 'Usuario creado';
    this.editing = null;
  }

  get currentUserId(): number | null {
    return this.currentUser ? this.currentUser.id : null;
  }
}
