import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TestPlan, TestPlanCreate } from '../../models';
import { TestPlanService } from '../../services/test-plan.service';

@Component({
  selector: 'app-test-plan-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="plan-form">
      <h2>{{ plan ? 'Editar' : 'Crear' }} Plan de Prueba</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.nombre" name="nombre" required minlength="5">
        </div>
        <div class="form-group">
          <label>Objetivo</label>
          <textarea class="form-control" [(ngModel)]="form.objetivo" name="objetivo"></textarea>
        </div>
        <div class="form-group">
          <label>Alcance</label>
          <textarea class="form-control" [(ngModel)]="form.alcance" name="alcance"></textarea>
        </div>
        <div class="form-group">
          <label>Criterios de Entrada</label>
          <textarea class="form-control" [(ngModel)]="form.criterios_entrada" name="entrada"></textarea>
        </div>
        <div class="form-group">
          <label>Criterios de Salida</label>
          <textarea class="form-control" [(ngModel)]="form.criterios_salida" name="salida"></textarea>
        </div>
        <div class="form-group">
          <label>Estrategia</label>
          <textarea class="form-control" [(ngModel)]="form.estrategia" name="estrategia"></textarea>
        </div>
        <div class="form-group">
          <label>Responsables</label>
          <input class="form-control" [(ngModel)]="form.responsables" name="responsables">
        </div>
        <div class="form-group d-flex gap-2">
          <div class="flex-fill">
            <label>Fecha Inicio</label>
            <input type="date" class="form-control" [(ngModel)]="form.fecha_inicio" name="fecha_inicio">
          </div>
          <div class="flex-fill">
            <label>Fecha Fin</label>
            <input type="date" class="form-control" [(ngModel)]="form.fecha_fin" name="fecha_fin">
          </div>
        </div>
        <div class="form-group">
          <label>Historias BDD</label>
          <textarea class="form-control" [(ngModel)]="form.historias_bdd" name="historias"></textarea>
        </div>
        <div class="mt-3">
          <button type="submit" class="btn btn-primary mr-2">Guardar</button>
          <button type="button" class="btn btn-secondary" (click)="cancel.emit()">Cancelar</button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .plan-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    .gap-2 { gap: 0.5rem; }
    textarea { resize: vertical; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class TestPlanFormComponent {
  @Input() plan: TestPlan | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: TestPlanCreate = {
    nombre: '',
    objetivo: '',
    alcance: '',
    criterios_entrada: '',
    criterios_salida: '',
    estrategia: '',
    responsables: '',
    fecha_inicio: '',
    fecha_fin: '',
    historias_bdd: ''
  };

  constructor(private service: TestPlanService) {}

  ngOnChanges() {
    if (this.plan) {
      this.form = { ...this.plan };
    } else {
      this.form = {
        nombre: '',
        objetivo: '',
        alcance: '',
        criterios_entrada: '',
        criterios_salida: '',
        estrategia: '',
        responsables: '',
        fecha_inicio: '',
        fecha_fin: '',
        historias_bdd: ''
      };
    }
  }

  submit() {
    const obs = this.plan ?
      this.service.updateTestPlan(this.plan.id, this.form) :
      this.service.createTestPlan(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
