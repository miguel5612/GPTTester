import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User, Role } from '../../models';
import { UserService } from '../../services/user.service';
import { RoleService } from '../../services/role.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Usuarios</h1>
      <table class="table" *ngIf="users.length > 0">
        <thead>
          <tr><th>Username</th><th>Rol</th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let u of users">
            <td>{{ u.username }}</td>
            <td>
              <select class="form-select" [(ngModel)]="u.role.id" (change)="changeRole(u)">
                <option *ngFor="let r of roles" [ngValue]="r.id">{{ r.name }}</option>
              </select>
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

  constructor(private userService: UserService, private roleService: RoleService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.roleService.getRoles().subscribe(rs => this.roles = rs);
    this.userService.getUsers().subscribe(us => this.users = us);
  }

  changeRole(user: User) {
    this.userService.updateUserRole(user.id, { role_id: user.role.id }).subscribe();
  }
}
