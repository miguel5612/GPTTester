import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PageElement, PageElementCreate, Page, Test, Action } from '../../models';
import { ElementService } from '../../services/element.service';
import { PageService } from '../../services/page.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-element-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="element-form">
      <h2>{{ element ? 'Editar' : 'Crear' }} Localizador</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Página</label>
          <select class="form-control" [(ngModel)]="form.page_id" name="page">
            <option *ngFor="let p of pages" [ngValue]="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="form-group">
          <label>Tipo</label>
          <input class="form-control" [(ngModel)]="form.tipo" name="tipo" required>
        </div>
        <div class="form-group">
          <label>Estrategia</label>
          <input class="form-control" [(ngModel)]="form.estrategia" name="estrategia" required>
        </div>
        <div class="form-group">
          <label>Valor</label>
          <input class="form-control" [(ngModel)]="form.valor" name="valor" required>
        </div>
        <div class="form-group">
          <label>Descripción</label>
          <input class="form-control" [(ngModel)]="form.descripcion" name="descripcion">
        </div>
        <div class="form-group">
          <label>Escenario (Test)</label>
          <select class="form-control" [(ngModel)]="testId" name="test">
            <option [ngValue]="null">--</option>
            <option *ngFor="let t of tests" [ngValue]="t.id">{{ t.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Acción</label>
          <select class="form-control" [(ngModel)]="actionId" name="action">
            <option [ngValue]="null">--</option>
            <option *ngFor="let a of actions" [ngValue]="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .element-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class ElementFormComponent {
  @Input() element: PageElement | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: PageElementCreate = { page_id: 0, name: '', tipo: '', estrategia: '', valor: '', descripcion: '' };
  pages: Page[] = [];
  tests: Test[] = [];
  actions: Action[] = [];
  testId: number | null = null;
  actionId: number | null = null;

  constructor(private service: ElementService, private pageService: PageService, private api: ApiService) {
    this.pageService.getPages().subscribe(p => this.pages = p);
    this.api.getTests().subscribe(t => this.tests = t);
    this.api.getActions().subscribe(a => this.actions = a);
  }

  ngOnChanges() {
    if (this.element) {
      this.form = { ...this.element };
    } else {
      this.form = { page_id: this.pages[0]?.id || 0, name: '', tipo: '', estrategia: '', valor: '', descripcion: '' };
    }
  }

  submit() {
    const obs = this.element ?
      this.service.updateElement(this.element.id, this.form) :
      this.service.createElement(this.form);
    obs.subscribe(el => {
      if (this.testId && this.actionId) {
        const assignment = { action_id: this.actionId, element_id: el.id, test_id: this.testId };
        this.service.createAssignment(assignment).subscribe(() => this.saved.emit());
      } else {
        this.saved.emit();
      }
    });
  }
}
