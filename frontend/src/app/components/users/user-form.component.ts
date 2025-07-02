import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User, UserCreate, Role } from '../../models';
import { UserService } from '../../services/user.service';
import { RoleService } from '../../services/role.service';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-body">
        <h3 class="card-title">{{ user ? 'Editar Usuario' : 'Nuevo Usuario' }}</h3>
        <form (ngSubmit)="save()">
          <div class="mb-3">
            <label class="form-label">Usuario</label>
            <input class="form-control" [(ngModel)]="form.username" name="username" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Contraseña</label>
            <input type="password" class="form-control" [(ngModel)]="form.password" name="password" [required]="!user" />
          </div>
          <div class="mb-3">
            <label class="form-label">Rol</label>
            <select class="form-select" [(ngModel)]="form.role_id" name="role_id" required>
              <option *ngFor="let r of roles" [ngValue]="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="active" [(ngModel)]="form.is_active" name="is_active" />
            <label class="form-check-label" for="active">Activo</label>
          </div>
          <div *ngIf="error" class="alert alert-danger">{{ error }}</div>
          <button class="btn btn-primary" type="submit" [disabled]="saving">Guardar</button>
          <button type="button" class="btn btn-secondary ms-2" (click)="cancel.emit()" [disabled]="saving">Cancelar</button>
        </form>
      </div>
    </div>
  `
})
export class UserFormComponent implements OnInit {
  @Input() user: User | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  roles: Role[] = [];
  saving = false;
  error = '';

  form: any = {
    username: '',
    password: '',
    role_id: null,
    is_active: true
  };

  constructor(private userService: UserService, private roleService: RoleService) {}

  ngOnInit() {
    this.roleService.getRoles().subscribe(rs => (this.roles = rs));
    if (this.user) {
      this.form = {
        username: this.user.username,
        password: '',
        role_id: this.user.role.id,
        is_active: this.user.is_active
      };
    }
  }

  save() {
    if (!this.form.username || (!this.user && !this.form.password) || !this.form.role_id) {
      this.error = 'Todos los campos son obligatorios';
      return;
    }
    this.saving = true;
    this.error = '';
    const obs = this.user
      ? this.userService.updateUser(this.user.id, this.form)
      : this.userService.createUser(this.form as UserCreate & { role_id: number; is_active: boolean });
    obs.subscribe({
      next: () => {
        this.saving = false;
        this.saved.emit();
      },
      error: (err) => {
        this.saving = false;
        this.error = err.error?.detail || 'Error al guardar';
      }
    });
  }
}
