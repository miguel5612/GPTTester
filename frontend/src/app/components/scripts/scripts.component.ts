import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Test } from '../../models';
import { TestCaseService } from '../../services/test-case.service';
import { ParameterDialogComponent } from './parameter-dialog.component';
import { TestCaseFormComponent } from '../test-cases/test-case-form.component';

@Component({
  selector: 'app-scripts',
  standalone: true,
  imports: [CommonModule, FormsModule, ParameterDialogComponent, TestCaseFormComponent],
  template: `
    <div class="main-panel">
      <h1>Gestión de Scripts</h1>
      <div class="filters mb-3">
        <input class="form-control mb-2" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="filter()">
        <div class="d-flex flex-wrap gap-2">
          <select class="form-control" [(ngModel)]="priority" (change)="filter()">
            <option value="">Prioridad</option>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
          <select class="form-control" [(ngModel)]="status" (change)="filter()">
            <option value="">Estado</option>
            <option value="creado">Creado</option>
            <option value="parametrizado">Parametrizado</option>
            <option value="listo">Listo para ejecutar</option>
          </select>
          <button class="btn btn-primary" (click)="newTest()">Nuevo</button>
        </div>
      </div>

      <table class="table table-bordered" *ngIf="filtered.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Prioridad</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let t of filtered">
            <td>{{ t.name }}</td>
            <td>{{ t.priority || '-' }}</td>
            <td>{{ t.status || 'creado' }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(t)">Editar</button>
              <button class="btn btn-sm btn-info mr-2" (click)="param(t)">Parametrizar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(t)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="filtered.length === 0" class="mt-3">No hay scripts.</div>

      <app-test-case-form *ngIf="showForm" [test]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-test-case-form>
      <app-parameter-dialog *ngIf="showParam" [testId]="paramId!" (saved)="onParamSaved()" (cancel)="showParam=false"></app-parameter-dialog>
    </div>
  `,
  styles: [`
    .filters { max-width: 600px; }
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class ScriptsComponent implements OnInit {
  tests: Test[] = [];
  filtered: Test[] = [];
  search = '';
  priority = '';
  status = '';

  showForm = false;
  editing: Test | null = null;

  showParam = false;
  paramId: number | null = null;

  constructor(private service: TestCaseService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getTestCases().subscribe(t => { this.tests = t; this.filter(); });
  }

  filter() {
    const term = this.search.toLowerCase();
    this.filtered = this.tests.filter(t => {
      const matchText = t.name.toLowerCase().includes(term) || (t.description || '').toLowerCase().includes(term);
      const matchPriority = this.priority ? t.priority === this.priority : true;
      const matchStatus = this.status ? t.status === this.status : true;
      return matchText && matchPriority && matchStatus;
    });
  }

  newTest() { this.editing = null; this.showForm = true; }
  edit(t: Test) { this.editing = t; this.showForm = true; }
  remove(t: Test) { if (confirm('¿Eliminar script?')) this.service.deleteTestCase(t.id).subscribe(() => this.load()); }

  onSaved() { this.showForm = false; this.load(); }

  param(t: Test) { this.paramId = t.id; this.showParam = true; }
  onParamSaved() { this.showParam = false; this.load(); }
}
