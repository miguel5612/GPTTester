import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Action, PageElement } from '../../models';
import { ElementService } from '../../services/element.service';
import { ActionService } from '../../services/action.service';
import { TestCaseService } from '../../services/test-case.service';

@Component({
  selector: 'app-parameter-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="parameter-form">
      <h3>Parametrizar Script</h3>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Elemento</label>
          <select class="form-control" [(ngModel)]="elementId" name="element">
            <option [ngValue]="null">--</option>
            <option *ngFor="let el of elements" [ngValue]="el.id">{{ el.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Acción</label>
          <select class="form-control" [(ngModel)]="actionId" name="action">
            <option [ngValue]="null">--</option>
            <option *ngFor="let a of actions" [ngValue]="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Parámetros (JSON)</label>
          <input class="form-control" [(ngModel)]="params" name="params">
        </div>
        <div class="mt-3">
          <button class="btn btn-primary mr-2" type="submit">Guardar</button>
          <button class="btn btn-secondary" type="button" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .parameter-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class ParameterDialogComponent implements OnInit {
  @Input() testId!: number;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  elements: PageElement[] = [];
  actions: Action[] = [];
  elementId: number | null = null;
  actionId: number | null = null;
  params = '';

  constructor(
    private elementService: ElementService,
    private actionService: ActionService,
    private testService: TestCaseService
  ) {}

  ngOnInit() {
    this.elementService.getElements().subscribe(e => this.elements = e);
    this.actionService.getActions().subscribe(a => this.actions = a);
  }

  submit() {
    if (!this.elementId || !this.actionId) return;
    let parametros: any;
    if (this.params) {
      try { parametros = JSON.parse(this.params); } catch { alert('JSON inválido'); return; }
    }
    this.elementService.addToTest(this.elementId, this.testId).subscribe(() => {
      this.actionService.createAssignment({
        action_id: this.actionId!,
        element_id: this.elementId!,
        test_id: this.testId,
        parametros
      }).subscribe(() => {
        this.testService.updateTestCase(this.testId, { status: 'parametrizado' } as any).subscribe(() => this.saved.emit());
      });
    });
  }
}
