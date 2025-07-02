import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>GPT Tester</h1>
          <p>Sistema de Automatización de Pruebas</p>
        </div>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="login-form">
          <div class="form-group">
            <label for="username">Usuario</label>
            <input 
              type="text" 
              id="username"
              class="form-control" 
              formControlName="username"
              placeholder="Ingrese su usuario"
              [class.is-invalid]="loginForm.get('username')?.invalid && loginForm.get('username')?.touched"
              autocomplete="username">
            <div class="invalid-feedback" *ngIf="loginForm.get('username')?.invalid && loginForm.get('username')?.touched">
              El usuario es requerido
            </div>
          </div>

          <div class="form-group">
            <label for="password">Contraseña</label>
            <input 
              type="password" 
              id="password"
              class="form-control" 
              formControlName="password"
              placeholder="Ingrese su contraseña"
              [class.is-invalid]="loginForm.get('password')?.invalid && loginForm.get('password')?.touched"
              autocomplete="current-password">
            <div class="invalid-feedback" *ngIf="loginForm.get('password')?.invalid && loginForm.get('password')?.touched">
              La contraseña es requerida
            </div>
          </div>

          <div class="error-message" *ngIf="errorMessage">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-block"
            [disabled]="loading || loginForm.invalid">
            <span *ngIf="!loading">Iniciar Sesión</span>
            <span *ngIf="loading">
              <i class="fas fa-spinner fa-spin"></i> Iniciando...
            </span>
          </button>
        </form>

        <div class="login-footer">
          <p>¿No tienes cuenta? <a routerLink="/register">Regístrate aquí</a></p>
          
          <div class="demo-users">
            <p class="demo-title">Usuarios de demostración:</p>
            <div class="demo-user" (click)="fillDemo('admin', 'admin123')">
              <i class="fas fa-user-shield"></i> admin / admin123 <span class="role">(Administrador)</span>
            </div>
            <div class="demo-user" (click)="fillDemo('service_manager', 'service_manager')">
              <i class="fas fa-user-tie"></i> service_manager <span class="role">(Gerente)</span>
            </div>
            <div class="demo-user" (click)="fillDemo('architect', 'architect')">
              <i class="fas fa-user-cog"></i> architect <span class="role">(Arquitecto)</span>
            </div>
            <div class="demo-user" (click)="fillDemo('test_automator', 'test_automator')">
              <i class="fas fa-user"></i> test_automator <span class="role">(Automatizador)</span>
            </div>
          </div>
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
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
    }

    .login-card {
      background: white;
      border-radius: 10px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      width: 100%;
      max-width: 400px;
      overflow: hidden;
    }

    .login-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }

    .login-header h1 {
      margin: 0;
      font-size: 2rem;
      font-weight: bold;
    }

    .login-header p {
      margin: 10px 0 0 0;
      opacity: 0.9;
      font-size: 0.9rem;
    }

    .login-form {
      padding: 30px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      margin-bottom: 5px;
      color: #333;
      font-weight: 500;
    }

    .form-control {
      width: 100%;
      padding: 10px 15px;
      border: 1px solid #ddd;
      border-radius: 5px;
      font-size: 16px;
      transition: border-color 0.3s;
    }

    .form-control:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .form-control.is-invalid {
      border-color: #dc3545;
    }

    .invalid-feedback {
      color: #dc3545;
      font-size: 0.875rem;
      margin-top: 5px;
    }

    .error-message {
      background: #f8d7da;
      color: #721c24;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.875rem;
    }

    .error-message i {
      margin-right: 5px;
    }

    .btn {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 5px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .login-footer {
      background: #f8f9fa;
      padding: 20px 30px;
      text-align: center;
      font-size: 0.875rem;
    }

    .login-footer a {
      color: #667eea;
      text-decoration: none;
      font-weight: 500;
    }

    .login-footer a:hover {
      text-decoration: underline;
    }

    .demo-users {
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid #dee2e6;
    }

    .demo-title {
      font-weight: 500;
      margin-bottom: 10px;
      color: #666;
    }

    .demo-user {
      background: #e9ecef;
      padding: 8px 12px;
      border-radius: 5px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 0.875rem;
    }

    .demo-user:hover {
      background: #dee2e6;
      transform: translateX(5px);
    }

    .demo-user i {
      margin-right: 8px;
      color: #667eea;
    }

    .demo-user .role {
      color: #666;
      font-size: 0.8rem;
    }

    @media (max-width: 480px) {
      .login-card {
        margin: 0;
        border-radius: 0;
        min-height: 100vh;
      }

      .login-container {
        padding: 0;
      }
    }
  `]
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  ngOnInit() {
    // Si ya está autenticado, redirigir
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  onSubmit() {
    if (this.loginForm.invalid) {
      Object.keys(this.loginForm.controls).forEach(key => {
        const control = this.loginForm.get(key);
        if (control) {
          control.markAsTouched();
        }
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        this.authService.getCurrentUser().subscribe({
          next: () => {
            this.router.navigate(['/workspace']);
          },
          error: () => {
            this.router.navigate(['/workspace']);
          }
        });
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.message || 'Error al iniciar sesión';
      }
    });
  }

  fillDemo(username: string, password: string) {
    this.loginForm.patchValue({ username, password });
  }
}
