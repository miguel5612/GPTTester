import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { LoginRequest } from '../../models';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-panel">
        <div class="login-header">
          <h1>Analista de Pruebas</h1>
          <p class="text-secondary">Sistema de Automatización</p>
        </div>
        
        <form (ngSubmit)="onLogin()" class="login-form">
          <div class="form-group">
            <label for="username">Usuario</label>
            <input 
              type="text" 
              id="username"
              class="form-control" 
              [(ngModel)]="credentials.username"
              name="username"
              placeholder="Ingrese su usuario"
              required>
          </div>
          
          <div class="form-group">
            <label for="password">Contraseña</label>
            <input 
              type="password" 
              id="password"
              class="form-control" 
              [(ngModel)]="credentials.password"
              name="password"
              placeholder="Ingrese su contraseña"
              required>
          </div>
          
          <button
            type="submit"
            class="btn-primary login-btn"
            [disabled]="isLoading">
            <span *ngIf="isLoading">Iniciando sesión...</span>
            <span *ngIf="!isLoading">Iniciar Sesión</span>
          </button>
        </form>

        <div class="login-footer">
          <p class="text-secondary">
            Usuario por defecto: <strong>admin</strong><br>
            Contraseña: <strong>admin</strong>
          </p>
          <button type="button" class="btn-link register-btn" (click)="router.navigate(['/register'])">Crear cuenta</button>
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

      p {
        font-size: 0.9rem;
        line-height: 1.5;
      }
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
export class LoginComponent {
  credentials: LoginRequest = {
    username: '',
    password: ''
  };
  
  isLoading = false;
  errorMessage = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  onLogin() {
    if (!this.credentials.username || !this.credentials.password) {
      this.errorMessage = 'Por favor ingrese usuario y contraseña';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.apiService.login(this.credentials).subscribe({
      next: () => {
        this.apiService.getCurrentUser().subscribe({
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
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = 'Usuario o contraseña incorrectos';
        console.error('Login error:', error);
      }
    });
  }
}
