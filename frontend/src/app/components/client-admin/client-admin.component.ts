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
      <label class="form-label w-100 mb-2">Buscar:
        <input class="form-control" placeholder="Buscar..." [(ngModel)]="search" />
      </label>
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
        <ul class="list-group mb-2">
          <li class="list-group-item" *ngFor="let h of paginatedHistory()">{{ h.client }} - {{ h.action }}</li>
        </ul>
        <nav>
          <ul class="pagination mb-0">
            <li class="page-item" [class.disabled]="historyPage === 1">
              <button class="page-link" (click)="historyPrev()">Anterior</button>
            </li>
            <li class="page-item"><span class="page-link">{{ historyPage }}</span></li>
            <li class="page-item" [class.disabled]="historyPageEnd">
              <button class="page-link" (click)="historyNext()" [disabled]="historyPageEnd">Siguiente</button>
            </li>
          </ul>
        </nav>
      </div>

      <app-client-form *ngIf="showForm" [client]="editing" (saved)="onSaved($event)" (cancel)="showForm=false"></app-client-form>

      <div class="modal fade show d-block" tabindex="-1" *ngIf="selectedProject" (click)="selectedProject=null">
        <div class="modal-dialog modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-content">
            <div class="modal-body">
              <app-project-analysts [projectId]="selectedProject.id" (updated)="onProjectAnalystsUpdated($event)" (close)="selectedProject=null"></app-project-analysts>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show" *ngIf="selectedProject"></div>

      <div class="modal fade show d-block" tabindex="-1" *ngIf="selectedClient" (click)="selectedClient=null">
        <div class="modal-dialog modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-content">
            <div class="modal-body">
              <app-client-analysts [clientId]="selectedClient.id" (updated)="onClientAnalystsUpdated($event)" (close)="selectedClient=null"></app-client-analysts>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show" *ngIf="selectedClient"></div>
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
  historyPage = 1;

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
  filteredHistory() {
    const term = this.search.toLowerCase();
    return this.history.filter(h =>
      h.client.toLowerCase().includes(term) || h.action.toLowerCase().includes(term)
    );
  }

  paginatedHistory() {
    const list = this.filteredHistory();
    const start = (this.historyPage - 1) * 15;
    return list.slice(start, start + 15);
  }

  get historyPageEnd(): boolean {
    return this.historyPage * 15 >= this.filteredHistory().length;
  }

  historyPrev() {
    if (this.historyPage > 1) this.historyPage--;
  }

  historyNext() {
    if (!this.historyPageEnd) this.historyPage++;
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
