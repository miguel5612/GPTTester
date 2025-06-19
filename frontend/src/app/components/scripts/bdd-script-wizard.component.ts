import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Actor } from '../../models';
import { ActorService } from '../../services/actor.service';
import { TestCaseService } from '../../services/test-case.service';

@Component({
  selector: 'app-bdd-script-wizard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Nuevo Script BDD</h1>

      <div class="stepper mb-3">
        <div class="step" [class.active]="step >= 1">1</div>
        <div class="step" [class.active]="step >= 2">2</div>
        <div class="step" [class.active]="step >= 3">3</div>
        <div class="step" [class.active]="step >= 4">4</div>
        <div class="step" [class.active]="step >= 5">5</div>
      </div>

      <div *ngIf="step === 1">
        <h3>Paso 1: Información básica</h3>
        <div class="form-group">
          <label>Nombre</label>
          <input class="form-control" [(ngModel)]="form.name" name="name" required>
        </div>
        <div class="form-group">
          <label>Actor</label>
          <select class="form-control" [(ngModel)]="form.actor_id" name="actor">
            <option [ngValue]="null">--</option>
            <option *ngFor="let a of actors" [ngValue]="a.id">{{ a.name }}</option>
          </select>
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
          <label>Tags</label>
          <input class="form-control" [(ngModel)]="form.tags" name="tags">
        </div>
      </div>

      <div *ngIf="step === 2">
        <h3>Paso 2: Given</h3>
        <textarea class="form-control" rows="5" [(ngModel)]="form.given" name="given"></textarea>
        <div class="mt-2">
          <button class="btn btn-sm btn-light me-1" *ngFor="let s of givenSnippets" (click)="insertSnippet('given', s)">{{s}}</button>
        </div>
      </div>

      <div *ngIf="step === 3">
        <h3>Paso 3: When</h3>
        <textarea class="form-control" rows="5" [(ngModel)]="form.when" name="when"></textarea>
        <div class="mt-2">
          <button class="btn btn-sm btn-light me-1" *ngFor="let s of whenSnippets" (click)="insertSnippet('when', s)">{{s}}</button>
        </div>
      </div>

      <div *ngIf="step === 4">
        <h3>Paso 4: Then</h3>
        <textarea class="form-control" rows="5" [(ngModel)]="form.then" name="then"></textarea>
        <div class="mt-2">
          <button class="btn btn-sm btn-light me-1" *ngFor="let s of thenSnippets" (click)="insertSnippet('then', s)">{{s}}</button>
        </div>
      </div>

      <div *ngIf="step === 5">
        <h3>Vista previa</h3>
        <pre [innerHTML]="preview"></pre>
      </div>

      <div class="mt-3">
        <button class="btn btn-secondary me-2" (click)="back()" *ngIf="step > 1">Atrás</button>
        <button class="btn btn-primary" (click)="next()" *ngIf="step < 5">Siguiente</button>
        <div *ngIf="step === 5">
          <button class="btn btn-primary me-2" (click)="save(false)">Guardar Borrador</button>
          <button class="btn btn-success" (click)="save(true)">Guardar Finalizado</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stepper { display:flex; gap:0.5rem; }
    .step { width:24px; height:24px; border-radius:50%; background:#ccc; color:#fff; display:flex; align-items:center; justify-content:center; font-size:12px; }
    .step.active { background:#3399FF; }
    .form-group { margin-bottom:1rem; }
    pre { background:#f8f9fa; padding:1rem; }
    .variable { color:#d63384; font-weight:bold; }
    .me-1 { margin-right:0.25rem; }
  `]
})
export class BddScriptWizardComponent implements OnInit {
  step = 1;
  actors: Actor[] = [];

  givenSnippets = ['el usuario está autenticado', 'existe un pedido {pedido}'];
  whenSnippets = ['hace clic en {boton}', 'ingresa {texto} en {campo}'];
  thenSnippets = ['se muestra {mensaje}', 'la página navega a {url}'];

  form = {
    name: '',
    actor_id: null as number | null,
    priority: '',
    tags: '',
    given: '',
    when: '',
    then: ''
  };

  constructor(
    private actorService: ActorService,
    private testService: TestCaseService,
    private router: Router
  ) {}

  ngOnInit() {
    this.actorService.getActors().subscribe(a => (this.actors = a));
  }

  insertSnippet(field: 'given' | 'when' | 'then', snippet: string) {
    this.form[field] += (this.form[field] ? '\n' : '') + snippet;
  }

  next() {
    if (this.validateStep()) {
      this.step++;
    }
  }

  back() {
    if (this.step > 1) this.step--;
  }

  validateStep(): boolean {
    if (this.step === 1) {
      return this.form.name.trim().length > 0;
    }
    if (this.step === 2) {
      return this.form.given.trim().length > 0;
    }
    if (this.step === 3) {
      return this.form.when.trim().length > 0;
    }
    if (this.step === 4) {
      return this.form.then.trim().length > 0;
    }
    return true;
  }

  get preview(): string {
    const replace = (t: string) => t.replace(/\{([^}]+)\}/g, '<span class="variable">{$1}</span>');
    return `Feature: ${this.form.name}\n` +
      `Given ${replace(this.form.given)}\n` +
      `When ${replace(this.form.when)}\n` +
      `Then ${replace(this.form.then)}`;
  }

  save(finalize: boolean) {
    const payload = {
      name: this.form.name,
      description: this.form.tags,
      actor_id: this.form.actor_id ?? undefined,
      priority: this.form.priority,
      given: this.form.given,
      when: this.form.when,
      then: this.form.then,
      status: finalize ? 'listo' : 'creado'
    } as any;
    this.testService.createTestCase(payload).subscribe(() => {
      alert('Script guardado');
      this.router.navigate(['/scripts']);
    });
  }
}
