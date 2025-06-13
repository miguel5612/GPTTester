import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UserCreate } from '../../models';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Registrar Usuario</h1>
      <form (ngSubmit)="save()" class="form">
        <div class="mb-3">
          <label class="form-label">Usuario</label>
          <input class="form-control" [(ngModel)]="form.username" name="username" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Contraseña</label>
          <input class="form-control" type="password" [(ngModel)]="form.password" name="password" required>
        </div>
        <button class="btn btn-primary" type="submit">Crear</button>
        <button class="btn btn-secondary ms-2" type="button" (click)="router.navigate(['/users'])">Cancelar</button>
      </form>
    </div>
  `
})
export class RegisterComponent {
  form: UserCreate = { username: '', password: '' };

  constructor(private service: UserService, public router: Router) {}

  save() {
    this.service.createUser(this.form).subscribe(() => {
      this.router.navigate(['/users']);
    });
  }
}
