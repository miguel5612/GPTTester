import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TestPlan } from '../../models';
import { TestPlanService } from '../../services/test-plan.service';
import { TestPlanFormComponent } from './test-plan-form.component';

@Component({
  selector: 'app-test-plans',
  standalone: true,
  imports: [CommonModule, FormsModule, TestPlanFormComponent],
  template: `
    <div class="main-panel">
      <h1>Planes de Prueba</h1>
      <div class="mb-3 d-flex gap-2">
        <input class="form-control" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="filter()">
        <button class="btn btn-primary" (click)="new()">Nuevo</button>
      </div>
      <table class="table table-bordered" *ngIf="filtered.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Objetivo</th>
            <th>Inicio</th>
            <th>Fin</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let p of filtered">
            <td>{{ p.nombre }}</td>
            <td>{{ p.objetivo || '-' }}</td>
            <td>{{ p.fecha_inicio || '-' }}</td>
            <td>{{ p.fecha_fin || '-' }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(p)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(p)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="filtered.length === 0">No hay planes de prueba.</div>

      <app-test-plan-form *ngIf="showForm" [plan]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-test-plan-form>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class TestPlansComponent implements OnInit {
  plans: TestPlan[] = [];
  filtered: TestPlan[] = [];
  search = '';
  showForm = false;
  editing: TestPlan | null = null;

  constructor(private service: TestPlanService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getTestPlans().subscribe(p => { this.plans = p; this.filter(); });
  }

  filter() {
    const term = this.search.toLowerCase();
    this.filtered = this.plans.filter(p => p.nombre.toLowerCase().includes(term));
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(p: TestPlan) {
    this.editing = p;
    this.showForm = true;
  }

  remove(p: TestPlan) {
    if (confirm('¿Eliminar plan de prueba?')) {
      this.service.deleteTestPlan(p.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
