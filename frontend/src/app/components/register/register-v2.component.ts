import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h1>Crear Cuenta</h1>
          <p>Únete a GPT Tester</p>
        </div>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="register-form">
          <div class="form-group">
            <label for="username">Usuario</label>
            <input 
              type="text" 
              id="username"
              class="form-control" 
              formControlName="username"
              placeholder="Elige un nombre de usuario"
              [class.is-invalid]="isFieldInvalid('username')">
            <div class="invalid-feedback" *ngIf="isFieldInvalid('username')">
              <span *ngIf="registerForm.get('username')?.errors?.['required']">El usuario es requerido</span>
              <span *ngIf="registerForm.get('username')?.errors?.['minlength']">Mínimo 3 caracteres</span>
            </div>
          </div>

          <div class="form-group">
            <label for="password">Contraseña</label>
            <input 
              type="password" 
              id="password"
              class="form-control" 
              formControlName="password"
              placeholder="Crea una contraseña segura"
              [class.is-invalid]="isFieldInvalid('password')">
            <div class="invalid-feedback" *ngIf="isFieldInvalid('password')">
              <span *ngIf="registerForm.get('password')?.errors?.['required']">La contraseña es requerida</span>
              <span *ngIf="registerForm.get('password')?.errors?.['minlength']">Mínimo 8 caracteres</span>
            </div>
            <div class="password-strength" *ngIf="registerForm.get('password')?.value">
              <div class="strength-bar" [class]="getPasswordStrength()"></div>
              <span class="strength-text">{{ getPasswordStrengthText() }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirmar Contraseña</label>
            <input 
              type="password" 
              id="confirmPassword"
              class="form-control" 
              formControlName="confirmPassword"
              placeholder="Confirma tu contraseña"
              [class.is-invalid]="isFieldInvalid('confirmPassword')">
            <div class="invalid-feedback" *ngIf="isFieldInvalid('confirmPassword')">
              <span *ngIf="registerForm.get('confirmPassword')?.errors?.['required']">Debes confirmar la contraseña</span>
              <span *ngIf="registerForm.errors?.['passwordMismatch'] && registerForm.get('confirmPassword')?.touched">
                Las contraseñas no coinciden
              </span>
            </div>
          </div>

          <div class="form-group">
            <label for="userType">Tipo de Usuario</label>
            <select 
              id="userType"
              class="form-control" 
              formControlName="user_type"
              [class.is-invalid]="isFieldInvalid('user_type')">
              <option value="">Selecciona tu rol</option>
              <option value="analyst">Analista de Pruebas / Automatizador</option>
              <option value="service_manager">Gerente de Servicios</option>
              <option value="architect">Arquitecto de Automatización</option>
            </select>
            <div class="invalid-feedback" *ngIf="isFieldInvalid('user_type')">
              Debes seleccionar un tipo de usuario
            </div>
          </div>

          <div class="role-description" *ngIf="registerForm.get('user_type')?.value">
            <i class="fas fa-info-circle"></i>
            <span [ngSwitch]="registerForm.get('user_type')?.value">
              <span *ngSwitchCase="'analyst'">
                <strong>Analista:</strong> Crea y ejecuta flujos de prueba, graba escenarios y automatiza procesos.
              </span>
              <span *ngSwitchCase="'service_manager'">
                <strong>Gerente:</strong> Gestiona clientes, proyectos y asigna analistas a los equipos.
              </span>
              <span *ngSwitchCase="'architect'">
                <strong>Arquitecto:</strong> Diseña componentes reutilizables y supervisa indicadores de calidad.
              </span>
            </span>
          </div>

          <div class="error-message" *ngIf="errorMessage">
            <i class="fas fa-exclamation-circle"></i>
            {{ errorMessage }}
          </div>

          <div class="success-message" *ngIf="successMessage">
            <i class="fas fa-check-circle"></i>
            {{ successMessage }}
          </div>

          <button 
            type="submit" 
            class="btn btn-primary btn-block"
            [disabled]="loading || registerForm.invalid">
            <span *ngIf="!loading">Crear Cuenta</span>
            <span *ngIf="loading">
              <i class="fas fa-spinner fa-spin"></i> Creando cuenta...
            </span>
          </button>
        </form>

        <div class="register-footer">
          <p>¿Ya tienes cuenta? <a routerLink="/login">Inicia sesión aquí</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .register-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
    }

    .register-card {
      background: white;
      border-radius: 10px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      width: 100%;
      max-width: 450px;
      overflow: hidden;
    }

    .register-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }

    .register-header h1 {
      margin: 0;
      font-size: 2rem;
      font-weight: bold;
    }

    .register-header p {
      margin: 10px 0 0 0;
      opacity: 0.9;
      font-size: 0.9rem;
    }

    .register-form {
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

    .password-strength {
      margin-top: 5px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .strength-bar {
      height: 4px;
      border-radius: 2px;
      flex: 1;
      transition: all 0.3s;
    }

    .strength-bar.weak {
      background: #dc3545;
      width: 33%;
    }

    .strength-bar.medium {
      background: #ffc107;
      width: 66%;
    }

    .strength-bar.strong {
      background: #28a745;
      width: 100%;
    }

    .strength-text {
      font-size: 0.75rem;
      color: #666;
    }

    .role-description {
      background: #e3f2fd;
      color: #1976d2;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .role-description i {
      margin-right: 8px;
    }

    .error-message {
      background: #f8d7da;
      color: #721c24;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.875rem;
    }

    .success-message {
      background: #d4edda;
      color: #155724;
      padding: 10px 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      font-size: 0.875rem;
    }

    .error-message i,
    .success-message i {
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

    .register-footer {
      background: #f8f9fa;
      padding: 20px 30px;
      text-align: center;
      font-size: 0.875rem;
    }

    .register-footer a {
      color: #667eea;
      text-decoration: none;
      font-weight: 500;
    }

    .register-footer a:hover {
      text-decoration: underline;
    }

    @media (max-width: 480px) {
      .register-card {
        margin: 0;
        border-radius: 0;
        min-height: 100vh;
      }

      .register-container {
        padding: 0;
      }
    }
  `]
})
export class RegisterComponent {
  registerForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
      user_type: ['', Validators.required]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  getPasswordStrength(): string {
    const password = this.registerForm.get('password')?.value || '';
    
    if (password.length < 8) return 'weak';
    
    let strength = 0;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    if (strength < 2) return 'weak';
    if (strength < 3) return 'medium';
    return 'strong';
  }

  getPasswordStrengthText(): string {
    const strength = this.getPasswordStrength();
    const texts: { [key: string]: string } = {
      'weak': 'Débil',
      'medium': 'Media',
      'strong': 'Fuerte'
    };
    return texts[strength] || '';
  }

  onSubmit() {
    if (this.registerForm.invalid) {
      Object.keys(this.registerForm.controls).forEach(key => {
        const control = this.registerForm.get(key);
        if (control) {
          control.markAsTouched();
        }
      });
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { confirmPassword, ...registerData } = this.registerForm.value;

    this.authService.register(registerData).subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = '¡Cuenta creada exitosamente! Redirigiendo...';
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.message || 'Error al crear la cuenta';
      }
    });
  }
}
