import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Action, ActionCreate } from '../../models';
import { ActionService } from '../../services/action.service';

@Component({
  selector: 'app-action-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="action-form">
      <h2>{{ action ? 'Editar' : 'Crear' }} Acción</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="form-group">
          <label>Tipo</label>
          <input class="form-control" [(ngModel)]="form.tipo" name="tipo" required>
        </div>
        <div class="form-group">
          <label>Argumentos (JSON)</label>
          <input class="form-control" [(ngModel)]="form.argumentos" name="args">
        </div>
        <div class="form-group">
          <label>Código</label>
          <textarea class="form-control" [(ngModel)]="form.codigo" name="code" rows="6"></textarea>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .action-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    textarea { font-family: monospace; resize: vertical; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class ActionFormComponent {
  @Input() action: Action | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: ActionCreate = { name: '', tipo: '', codigo: '', argumentos: '' };

  constructor(private service: ActionService) {}

  ngOnChanges() {
    if (this.action) {
      this.form = { ...this.action };
    } else {
      this.form = { name: '', tipo: '', codigo: '', argumentos: '' };
    }
  }

  submit() {
    const obs = this.action ?
      this.service.updateAction(this.action.id, this.form) :
      this.service.createAction(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
