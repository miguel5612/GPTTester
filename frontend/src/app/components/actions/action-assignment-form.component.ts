import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActionAssignmentCreate, PageElement, Test } from '../../models';
import { ActionService } from '../../services/action.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-action-assignment-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="assignment-form">
      <h3>Asociar Acción</h3>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Elemento</label>
          <select class="form-control" [(ngModel)]="form.element_id" name="element">
            <option *ngFor="let el of elements" [ngValue]="el.id">{{ el.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Test Case</label>
          <select class="form-control" [(ngModel)]="form.test_id" name="test">
            <option *ngFor="let t of tests" [ngValue]="t.id">{{ t.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Parámetros (JSON)</label>
          <input class="form-control" [(ngModel)]="params" name="params">
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .assignment-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class ActionAssignmentFormComponent {
  @Input() actionId!: number;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  elements: PageElement[] = [];
  tests: Test[] = [];
  params = '';
  form: ActionAssignmentCreate = { action_id: 0, element_id: 0, test_id: 0 };

  constructor(private service: ActionService, private api: ApiService) {
    this.api.getElements().subscribe(e => this.elements = e);
    this.api.getTests().subscribe(t => this.tests = t);
  }

  ngOnChanges() {
    this.form.action_id = this.actionId;
  }

  submit() {
    if (this.params) {
      try {
        this.form.parametros = JSON.parse(this.params);
      } catch {
        alert('Formato de parámetros inválido');
        return;
      }
    } else {
      delete this.form.parametros;
    }
    this.form.action_id = this.actionId;
    this.service.createAssignment(this.form).subscribe(() => this.saved.emit());
  }
}
