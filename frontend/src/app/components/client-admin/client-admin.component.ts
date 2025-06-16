import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { ClientService } from '../../services/client.service';
import { ProjectService } from '../../services/project.service';
import { Client, Project, User } from '../../models';
import { ClientFormComponent } from './client-form.component';
import { ProjectAnalystsComponent } from './project-analysts.component';
import { ClientAnalystsComponent } from './client-analysts.component';

@Component({
  selector: 'app-client-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, ClientFormComponent, ProjectAnalystsComponent, ClientAnalystsComponent],
  template: `
    <div class="main-panel">
      <h1>Administración de Clientes</h1>
      <button class="btn btn-primary mb-3" (click)="new()">Nuevo Cliente</button>
      <div *ngFor="let c of clients" class="mb-4">
        <h3>
          {{ c.name }}
          <button class="btn btn-sm btn-secondary ms-2" (click)="edit(c)">Editar</button>
          <button class="btn btn-sm btn-danger ms-2" (click)="remove(c)">Eliminar</button>
          <button class="btn btn-sm btn-info ms-2" (click)="manageClientAnalysts(c)">Analistas</button>
        </h3>
        <ul class="list-group">
          <li class="list-group-item" *ngFor="let p of projectsByClient(c.id)">
            {{ p.name }} - Analistas:
            <span *ngFor="let a of p.analysts; let i = index">
              {{ a.username }}<span *ngIf="i < p.analysts.length - 1">, </span>
            </span>
            <button class="btn btn-sm btn-info ms-2" (click)="manageAnalysts(p)">Analistas</button>
          </li>
        </ul>
      </div>

      <app-client-form *ngIf="showForm" [client]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-client-form>
      <app-project-analysts *ngIf="selectedProject" [projectId]="selectedProject.id" (updated)="loadData()" (close)="selectedProject=null"></app-project-analysts>
      <app-client-analysts *ngIf="selectedClient" [clientId]="selectedClient.id" (updated)="loadData()" (close)="selectedClient=null"></app-client-analysts>
    </div>
  `
})
export class ClientAdminComponent implements OnInit {
  clients: Client[] = [];
  projects: Project[] = [];
  users: User[] = [];
  showForm = false;
  editing: Client | null = null;
  selectedProject: Project | null = null;
  selectedClient: Client | null = null;

  constructor(
    private api: ApiService,
    private clientService: ClientService,
    private projectService: ProjectService
  ) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.clientService.getClients().subscribe(cs => (this.clients = cs));
    this.projectService.getProjects().subscribe(ps => (this.projects = ps));
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

  manageClientAnalysts(c: Client) {
    this.selectedClient = c;
  }

  manageAnalysts(p: Project) {
    this.selectedProject = p;
  }

  onSaved() {
    this.showForm = false;
    this.loadData();
  }
}
