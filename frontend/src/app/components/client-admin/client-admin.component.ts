import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ClientService } from '../../services/client.service';
import { Client, Project, User } from '../../models';
import { ClientFormComponent } from './client-form.component';

@Component({
  selector: 'app-client-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, ClientFormComponent],
  template: `
    <div class="main-panel">
      <h1>Administración de Clientes</h1>
      <button class="btn btn-primary mb-3" (click)="new()">Nuevo Cliente</button>
      <div *ngFor="let c of clients" class="mb-4">
        <h3>
          {{ c.name }}
          <button class="btn btn-sm btn-secondary ms-2" (click)="edit(c)">Editar</button>
          <button class="btn btn-sm btn-danger ms-2" (click)="remove(c)">Eliminar</button>
        </h3>
        <ul class="list-group">
          <li class="list-group-item" *ngFor="let p of projectsByClient(c.id)">
            {{ p.name }} - Analistas:
            <span *ngFor="let a of p.analysts; let i = index">
              {{ a.username }}<span *ngIf="i < p.analysts.length - 1">, </span>
            </span>
          </li>
        </ul>
      </div>

      <app-client-form *ngIf="showForm" [client]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-client-form>
    </div>
  `
})
export class ClientAdminComponent implements OnInit {
  clients: Client[] = [];
  projects: Project[] = [];
  users: User[] = [];
  showForm = false;
  editing: Client | null = null;

  constructor(private api: ApiService, private clientService: ClientService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.clientService.getClients().subscribe(cs => (this.clients = cs));
    this.api.getProjects().subscribe(ps => (this.projects = ps));
    this.api.getUsers().subscribe(us => (this.users = us));
  }

  projectsByClient(clientId: number): Project[] {
    return this.projects.filter(p => p.client_id === clientId);
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(c: Client) {
    this.editing = c;
    this.showForm = true;
  }

  remove(c: Client) {
    if (confirm('¿Eliminar cliente?')) {
      this.clientService.deleteClient(c.id).subscribe(() => this.loadData());
    }
  }

  onSaved() {
    this.showForm = false;
    this.loadData();
  }
}
