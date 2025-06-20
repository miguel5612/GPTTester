import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { User, Role } from '../../models';
import { UserService } from '../../services/user.service';
import { RoleService } from '../../services/role.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="main-panel">
      <h1>Usuarios</h1>
      <button class="btn btn-primary mb-2" routerLink="/register">Registrar Usuario</button>
      <table class="table" *ngIf="users.length > 0">
        <thead>
          <tr><th>Username</th><th>Rol</th><th>Último Login</th><th>Activo</th><th></th></tr>
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
            <td>{{ u.is_active ? 'Sí' : 'No' }}</td>
            <td>
              <button class="btn btn-sm btn-secondary" (click)="toggleActive(u)" [disabled]="u.id === currentUserId">
                {{ u.is_active ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="users.length === 0">No hay usuarios.</div>
    </div>
  `
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  roles: Role[] = [];
  currentUser: User | null = null;

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

  changeRole(user: User) {
    this.userService.updateUserRole(user.id, { role_id: user.role.id }).subscribe();
  }

  toggleActive(user: User) {
    this.userService.updateUserActive(user.id, !user.is_active).subscribe(u => user.is_active = u.is_active);
  }

  get currentUserId(): number | null {
    return this.currentUser ? this.currentUser.id : null;
  }
}
