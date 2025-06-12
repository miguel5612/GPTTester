import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TestCaseService } from '../../services/test-case.service';
import { ApiService } from '../../services/api.service';
import { Test, TestPlan } from '../../models';
import { TestCaseFormComponent } from './test-case-form.component';

@Component({
  selector: 'app-test-cases',
  standalone: true,
  imports: [CommonModule, FormsModule, TestCaseFormComponent],
  template: `
    <div class="main-panel">
      <h1>Casos de Prueba</h1>
      <div class="filters mb-3">
        <input class="form-control mb-2" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="loadTests()">
        <div class="d-flex flex-wrap gap-2">
          <select class="form-control" [(ngModel)]="priority" (change)="loadTests()">
            <option value="">Prioridad</option>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
          <select class="form-control" [(ngModel)]="status" (change)="loadTests()">
            <option value="">Estado</option>
            <option value="pendiente">Pendiente</option>
            <option value="en progreso">En Progreso</option>
            <option value="completado">Completado</option>
          </select>
          <select class="form-control" [(ngModel)]="planId" (change)="loadTests()">
            <option [ngValue]="null">Plan de prueba</option>
            <option *ngFor="let p of plans" [ngValue]="p.id">{{ p.nombre }}</option>
          </select>
          <button class="btn btn-primary" (click)="newTest()">Nuevo</button>
        </div>
      </div>

      <table class="table table-bordered" *ngIf="tests.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Prioridad</th>
            <th>Estado</th>
            <th>Plan</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let t of tests">
            <td>{{ t.name }}</td>
            <td>{{ t.priority || '-' }}</td>
            <td>{{ t.status || '-' }}</td>
            <td>{{ planName(t.test_plan_id) }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(t)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(t)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="tests.length === 0" class="mt-3">No hay casos de prueba.</div>

      <app-test-case-form *ngIf="showForm" [test]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-test-case-form>
    </div>
  `,
  styles: [`
    .filters { max-width: 600px; }
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class TestCasesComponent implements OnInit {
  tests: Test[] = [];
  plans: TestPlan[] = [];
  search = '';
  priority = '';
  status = '';
  planId: number | null = null;

  showForm = false;
  editing: Test | null = null;

  constructor(private service: TestCaseService, private api: ApiService) {}

  ngOnInit() {
    this.loadPlans();
    this.loadTests();
  }

  loadPlans() {
    this.api.getTestPlans().subscribe(pl => this.plans = pl);
  }

  loadTests() {
    this.service.getTestCases(this.search || undefined, this.priority || undefined, this.status || undefined, this.planId !== null ? this.planId : undefined)
      .subscribe(t => this.tests = t);
  }

  planName(id?: number | null): string {
    const plan = this.plans.find(p => p.id === id);
    return plan ? plan.nombre : '-';
  }

  newTest() {
    this.editing = null;
    this.showForm = true;
  }

  edit(test: Test) {
    this.editing = test;
    this.showForm = true;
  }

  remove(test: Test) {
    if (confirm('¿Eliminar caso de prueba?')) {
      this.service.deleteTestCase(test.id).subscribe(() => this.loadTests());
    }
  }

  onSaved() {
    this.showForm = false;
    this.loadTests();
  }
}
