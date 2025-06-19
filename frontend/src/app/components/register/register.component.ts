import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UserCreate, LoginRequest } from '../../models';
import { UserService } from '../../services/user.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-panel">
        <div class="login-header">
          <h1>Crear Cuenta</h1>
          <p class="text-secondary">Sistema de Automatización</p>
        </div>

        <form (ngSubmit)="save()" class="login-form">
          <div class="form-group">
            <label>Usuario</label>
            <input class="form-control" [(ngModel)]="form.username" name="username" required>
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input type="password" class="form-control" [(ngModel)]="form.password" name="password" required>
          </div>

          <button type="submit" class="btn-primary login-btn" [disabled]="isLoading">
            <span *ngIf="isLoading">Creando...</span>
            <span *ngIf="!isLoading">Registrarse</span>
          </button>
        </form>

        <div class="login-footer">
          <button type="button" class="btn-link register-btn" (click)="router.navigate(['/login'])">Ya tengo cuenta</button>
        </div>

        <div *ngIf="errorMessage" class="alert alert-error alert-fixed">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .login-panel {
      background: var(--panel-bg);
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      padding: 3rem;
      width: 100%;
      max-width: 400px;
      animation: panelEntrance 0.6s ease-out;
    }

    .login-header {
      text-align: center;
      margin-bottom: 2rem;

      h1 {
        color: var(--title-color);
        margin-bottom: 0.5rem;
        font-size: 2rem;
      }
    }

    .form-group {
      margin-bottom: 1.5rem;

      label {
        display: block;
        margin-bottom: 0.5rem;
        color: var(--subtitle-color);
        font-weight: 500;
      }
    }

    .login-btn {
      width: 100%;
      padding: 1rem;
      font-size: 1.1rem;
      margin-top: 1rem;
    }

    .alert {
      padding: 0.75rem;
      border-radius: 6px;
      margin-bottom: 1rem;

      &.alert-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
      }
    }

    .login-footer {
      text-align: center;
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border-color);

      .register-btn {
        margin-top: 1rem;
        background: none;
        border: none;
        color: var(--btn-primary);
        cursor: pointer;
      }
    }

    .alert-fixed {
      position: fixed;
      bottom: 1rem;
      right: 1rem;
      z-index: 1000;
    }
  `]
})
export class RegisterComponent {
  form: UserCreate = { username: '', password: '' };
  isLoading = false;
  errorMessage = '';

  constructor(
    private service: UserService,
    private api: ApiService,
    public router: Router
  ) {}

  save() {
    if (!this.form.username || !this.form.password) {
      this.errorMessage = 'Usuario y contraseña requeridos';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.service.createUser(this.form).subscribe({
      next: () => {
        const creds: LoginRequest = { username: this.form.username, password: this.form.password };
        this.api.login(creds).subscribe({
          next: () => {
            this.api.getCurrentUser().subscribe({
              next: (user) => {
                const role = user.role?.name || '';
                this.isLoading = false;
                if (role === 'Administrador') {
                  this.router.navigate(['/users']);
                } else if (role === 'Arquitecto de Automatización' || role === 'Automation Engineer') {
                  this.router.navigate(['/actions']);
                } else if (role === 'Gerente de servicios') {
                  this.router.navigate(['/client-admin']);
                } else {
                  this.router.navigate(['/dashboard']);
                }
              },
              error: () => {
                this.isLoading = false;
                this.router.navigate(['/dashboard']);
              }
            });
          },
          error: () => {
            this.isLoading = false;
            this.errorMessage = 'Error al iniciar sesión';
          }
        });
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Nombre de usuario en uso o contraseña insegura';
        console.error('Register error:', err);
      }
    });
  }
}
