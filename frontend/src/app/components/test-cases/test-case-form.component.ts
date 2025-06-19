import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Test, TestCreate, TestPlan, Actor } from '../../models';
import { TestCaseService } from '../../services/test-case.service';
import { ApiService } from '../../services/api.service';
import { ActorService } from '../../services/actor.service';
import { WorkspaceService } from '../../services/workspace.service';

@Component({
  selector: 'app-test-case-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="test-form">
      <h2>{{ test ? 'Editar' : 'Crear' }} Caso de Prueba</h2>
      <form (ngSubmit)="submit()">
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="form-group">
          <label>Descripción</label>
          <textarea class="form-control" [(ngModel)]="form.description" name="description"></textarea>
        </div>
        <div class="form-group">
          <label>Dado (Given)</label>
          <textarea class="form-control" [(ngModel)]="form.given" name="given"></textarea>
        </div>
        <div class="form-group">
          <label>Cuando (When)</label>
          <textarea class="form-control" [(ngModel)]="form.when" name="when"></textarea>
        </div>
        <div class="form-group">
          <label>Entonces (Then)</label>
          <textarea class="form-control" [(ngModel)]="form.then" name="then"></textarea>
        </div>
        <div class="form-group">
          <label>Prioridad</label>
          <select class="form-control" [(ngModel)]="form.priority" name="priority">
            <option value="">--</option>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </div>
        <div class="form-group">
          <label>Estado</label>
          <select class="form-control" [(ngModel)]="form.status" name="status">
            <option value="">--</option>
            <option value="pendiente">Pendiente</option>
            <option value="en progreso">En Progreso</option>
            <option value="completado">Completado</option>
          </select>
        </div>
        <div class="form-group">
          <label>Actor</label>
          <select class="form-control" [(ngModel)]="form.actor_id" name="actor">
            <option [ngValue]="null">--</option>
            <option *ngFor="let a of actors" [ngValue]="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Plan de Prueba</label>
          <select class="form-control" [(ngModel)]="form.test_plan_id" name="plan">
            <option [ngValue]="null">--</option>
            <option *ngFor="let plan of plans" [ngValue]="plan.id">{{ plan.nombre }}</option>
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
    .test-form { padding: 1rem; }
    .form-group { margin-bottom: 1rem; }
    textarea { resize: vertical; }
    .mr-2 { margin-right: 0.5rem; }
  `]
})
export class TestCaseFormComponent {
  @Input() test: Test | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  plans: TestPlan[] = [];
  actors: Actor[] = [];

  form: TestCreate = {
    name: '',
    description: '',
    given: '',
    when: '',
    then: '',
    priority: '',
    status: '',
    test_plan_id: undefined,
    actor_id: undefined
  };

  constructor(
    private service: TestCaseService,
    private api: ApiService,
    private actorsService: ActorService,
    private workspace: WorkspaceService
  ) {
    this.api.getTestPlans().subscribe(pl => this.plans = pl);
    if (this.workspace.clientId) {
      this.actorsService.getActors(this.workspace.clientId).subscribe(a => (this.actors = a));
    }
  }

  ngOnChanges() {
    if (this.test) {
      this.form = { ...this.test };
    } else {
      this.form = {
        name: '',
        description: '',
        given: '',
        when: '',
        then: '',
        priority: '',
        status: '',
        test_plan_id: undefined,
        actor_id: undefined
      };
    }
  }

  submit() {
    const obs = this.test ?
      this.service.updateTestCase(this.test.id, this.form) :
      this.service.createTestCase(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
