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
      <input class="form-control mb-2" placeholder="Buscar..." [(ngModel)]="search" />
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <a class="nav-link" [class.active]="tab==='active'" (click)="tab='active'">Activos</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" [class.active]="tab==='inactive'" (click)="tab='inactive'">Inactivos</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" [class.active]="tab==='history'" (click)="tab='history'">Historial</a>
        </li>
      </ul>
      <div *ngIf="tab!=='history'">
        <button class="btn btn-primary mb-3" (click)="new()">Nuevo Cliente</button>
        <div *ngFor="let c of filteredClients()" class="mb-4">
        <h3>
          {{ c.name }}
          <button class="btn btn-sm btn-secondary ms-2" (click)="edit(c)">Editar</button>
          <button class="btn btn-sm btn-danger ms-2" (click)="remove(c)">Inactivar</button>
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
      </div>
      <div *ngIf="tab==='history'">
        <ul class="list-group">
          <li class="list-group-item" *ngFor="let h of history">{{ h.client }} - {{ h.action }}</li>
        </ul>
      </div>

      <app-client-form *ngIf="showForm" [client]="editing" (saved)="onSaved($event)" (cancel)="showForm=false"></app-client-form>
      <app-project-analysts *ngIf="selectedProject" [projectId]="selectedProject.id" (updated)="onProjectAnalystsUpdated($event)" (close)="selectedProject=null"></app-project-analysts>
      <app-client-analysts *ngIf="selectedClient" [clientId]="selectedClient.id" (updated)="onClientAnalystsUpdated($event)" (close)="selectedClient=null"></app-client-analysts>
  `
})
export class ClientAdminComponent implements OnInit {
  clients: Client[] = [];
  projects: Project[] = [];
  showForm = false;
  editing: Client | null = null;
  selectedProject: Project | null = null;
  selectedClient: Client | null = null;
  search = '';
  tab: 'active' | 'inactive' | 'history' = 'active';
  history: { client: string; action: string }[] = [];

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
  }

  filteredClients(): Client[] {
    const term = this.search.toLowerCase();
    return this.clients
      .filter(c => c.name.toLowerCase().includes(term))
      .filter(c =>
        this.tab === 'active'
          ? c.is_active
          : this.tab === 'inactive'
          ? !c.is_active
          : true
      );
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
    if (confirm('¿Inactivar cliente?')) {
      this.clientService.deleteClient(c.id).subscribe(() => {
        this.history.push({ client: c.name, action: 'inactivado' });
        this.loadData();
      });
    }
  }

  manageAnalysts(p: Project) {
    this.selectedProject = p;
  }

  manageClientAnalysts(c: Client) {
    this.selectedClient = c;
  }

  onProjectAnalystsUpdated(e: { action: string; user: User }) {
    if (this.selectedProject) {
      const clientName = this.clients.find(cl => cl.id === this.selectedProject!.client_id)?.name || '';
      this.history.push({ client: clientName, action: `${e.action} (${e.user.username}) en proyecto ${this.selectedProject.name}` });
      this.loadData();
    }
  }

  onClientAnalystsUpdated(e: { action: string; user: User }) {
    if (this.selectedClient) {
      this.history.push({ client: this.selectedClient.name, action: `${e.action} (${e.user.username})` });
      this.loadData();
    }
  }

  onSaved(c: Client) {
    this.showForm = false;
    this.loadData();
    const action = this.editing ? 'actualizado' : 'creado';
    this.history.push({ client: c.name, action });
  }
}
