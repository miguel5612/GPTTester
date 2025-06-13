import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Actor, Client } from '../../models';
import { ActorService } from '../../services/actor.service';
import { ApiService } from '../../services/api.service';
import { ActorFormComponent } from './actor-form.component';

@Component({
  selector: 'app-actors',
  standalone: true,
  imports: [CommonModule, FormsModule, ActorFormComponent],
  template: `
    <div class="main-panel">
      <h1>Gestión de Actores</h1>
      <div class="mb-3">
        <label>Cliente</label>
        <select class="form-select" [(ngModel)]="selectedClient" (change)="load()">
          <option [ngValue]="null">Todos</option>
          <option *ngFor="let c of clients" [ngValue]="c.id">{{ c.name }}</option>
        </select>
      </div>
      <button class="btn btn-primary mb-2" (click)="new()">Nuevo Actor</button>
      <table class="table" *ngIf="actors.length > 0">
        <thead>
          <tr><th>Nombre</th><th>Cliente</th><th></th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let a of actors">
            <td>{{ a.name }}</td>
            <td>{{ clientName(a.client_id) }}</td>
            <td>
              <button class="btn btn-sm btn-secondary me-2" (click)="edit(a)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(a)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="actors.length === 0">No hay actores.</div>

      <app-actor-form *ngIf="showForm" [actor]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-actor-form>
    </div>
  `
})
export class ActorsComponent implements OnInit {
  actors: Actor[] = [];
  clients: Client[] = [];
  selectedClient: number | null = null;
  showForm = false;
  editing: Actor | null = null;

  constructor(private service: ActorService, private api: ApiService) {}

  ngOnInit() {
    this.api.getClients().subscribe(c => this.clients = c);
    this.load();
  }

  load() {
    this.service.getActors(this.selectedClient || undefined).subscribe(a => this.actors = a);
  }

  clientName(id: number): string {
    const c = this.clients.find(c => c.id === id);
    return c ? c.name : '';
  }

  new() { this.editing = null; this.showForm = true; }

  edit(a: Actor) { this.editing = a; this.showForm = true; }

  remove(a: Actor) {
    if (confirm('¿Eliminar actor?')) {
      this.service.deleteActor(a.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
