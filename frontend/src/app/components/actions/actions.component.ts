import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Action } from '../../models';
import { ActionService } from '../../services/action.service';
import { ActionFormComponent } from './action-form.component';
import { ActionAssignmentFormComponent } from './action-assignment-form.component';

@Component({
  selector: 'app-actions',
  standalone: true,
  imports: [CommonModule, FormsModule, ActionFormComponent, ActionAssignmentFormComponent],
  template: `
    <div class="main-panel">
      <h1>Acciones Automatizadas</h1>
      <div class="d-flex flex-wrap gap-2 mb-3">
        <input class="form-control" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="load()">
        <input class="form-control" [(ngModel)]="tipo" placeholder="Tipo" (ngModelChange)="load()">
        <button class="btn btn-primary" (click)="new()">Nueva</button>
      </div>
      <table class="table table-bordered" *ngIf="actions.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Tipo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let a of actions">
            <td>{{ a.name }}</td>
            <td>{{ a.tipo }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(a)">Editar</button>
              <button class="btn btn-sm btn-info mr-2" (click)="assign(a)">Asignar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(a)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="actions.length === 0">No hay acciones.</div>

      <app-action-form *ngIf="showForm" [action]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-action-form>
      <app-action-assignment-form *ngIf="assigning" [actionId]="assignId!" (saved)="onAssigned()" (cancel)="assigning=false"></app-action-assignment-form>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class ActionsComponent implements OnInit {
  actions: Action[] = [];
  search = '';
  tipo = '';
  showForm = false;
  editing: Action | null = null;

  assigning = false;
  assignId: number | null = null;

  constructor(private service: ActionService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getActions(this.search || undefined, this.tipo || undefined).subscribe(a => this.actions = a);
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(a: Action) {
    this.editing = a;
    this.showForm = true;
  }

  remove(a: Action) {
    if (confirm('¿Eliminar acción?')) {
      this.service.deleteAction(a.id).subscribe(() => this.load());
    }
  }

  assign(a: Action) {
    this.assignId = a.id;
    this.assigning = true;
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }

  onAssigned() {
    this.assigning = false;
  }
}
