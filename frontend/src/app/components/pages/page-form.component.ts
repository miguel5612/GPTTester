import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Page, PageCreate } from '../../models';
import { PageService } from '../../services/page.service';

@Component({
  selector: 'app-page-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-form">
      <h2>{{ page ? 'Editar' : 'Crear' }} Página</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .page-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class PageFormComponent {
  @Input() page: Page | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: PageCreate = { name: '' };

  constructor(private service: PageService) {}

  ngOnChanges() {
    if (this.page) {
      this.form = { name: this.page.name };
    } else {
      this.form = { name: '' };
    }
  }

  submit() {
    const obs = this.page ?
      this.service.updatePage(this.page.id, this.form) :
      this.service.createPage(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
