import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Client, Project, User } from '../../models';
import { ClientService } from '../../services/client.service';
import { ProjectService } from '../../services/project.service';
import { ApiService } from '../../services/api.service';
import { ClientAnalystsComponent } from '../client-admin/client-analysts.component';
import { ProjectAnalystsComponent } from '../client-admin/project-analysts.component';
import { ClientProjectsComponent } from '../client-admin/client-projects.component';

@Component({
  selector: 'app-service-manager',
  standalone: true,
  imports: [CommonModule, FormsModule, ClientAnalystsComponent, ProjectAnalystsComponent, ClientProjectsComponent],
  template: `
    <div class="main-panel">
      <h1>Gerencia de Servicio</h1>
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item"><a class="nav-link" [class.active]="tab==='clients'" (click)="tab='clients'">Clientes</a></li>
        <li class="nav-item"><a class="nav-link" [class.active]="tab==='projects'" (click)="tab='projects'">Proyectos</a></li>
        <li class="nav-item"><a class="nav-link" [class.active]="tab==='team'" (click)="tab='team'">Equipo</a></li>
      </ul>

      <div *ngIf="tab==='clients'">
        <label class="form-label w-100 mb-2">Nuevo cliente:
          <input class="form-control" [(ngModel)]="newClient" placeholder="Nombre" />
        </label>
        <button class="btn btn-primary mb-3" (click)="createClient()">Crear</button>
        <ul class="list-group">
          <li class="list-group-item d-flex justify-content-between align-items-center" *ngFor="let c of clients">
            {{c.name}} <span>
              <button class="btn btn-sm btn-info" (click)="openClientAnalysts(c)">Analistas</button>
              <button class="btn btn-sm btn-warning" (click)="openProjects(c)">Proyectos</button>
            </span>
          </li>
        </ul>
      </div>

      <div *ngIf="tab==='projects'">
        <label class="form-label">Cliente:
          <select class="form-select" [(ngModel)]="filterClient">
            <option [ngValue]="0">Todos</option>
            <option *ngFor="let c of clients" [ngValue]="c.id">{{c.name}}</option>
          </select>
        </label>
        <ul class="list-group">
          <li class="list-group-item d-flex justify-content-between align-items-center" *ngFor="let p of filteredProjects()">
            {{p.name}}
            <span>
              <button class="btn btn-sm btn-info" (click)="openProjectAnalysts(p)">Analistas</button>
            </span>
          </li>
        </ul>
      </div>

      <div *ngIf="tab==='team'">
        <table class="table">
          <thead><tr><th>Analista</th><th>Proyectos</th><th>Carga</th><th>Reasignar</th></tr></thead>
          <tbody>
            <tr *ngFor="let a of team()">
              <td>{{a.user.username}}</td>
              <td>{{projectNames(a.projects)}}</td>
              <td>{{a.load}}</td>
              <td>
                <select class="form-select form-select-sm mb-1" [(ngModel)]="reassignTarget[a.user.id]">
                  <option *ngFor="let p of projects" [ngValue]="p.id">{{p.name}}</option>
                </select>
                <button class="btn btn-sm btn-secondary" (click)="reassign(a.user, reassignTarget[a.user.id])">Mover</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-4">
        <h3>Métricas</h3>
        <p>Proyectos activos: {{activeProjects}}</p>
        <p>Analistas asignados: {{assignedAnalysts}}</p>
        <p>Capacidad del equipo: {{teamCapacity}}</p>
      </div>

      <app-client-analysts [clientId]="selectedClient!.id" (updated)="loadData()" (close)="selectedClient=null" *ngIf="selectedClient"></app-client-analysts>
      <app-project-analysts [projectId]="selectedProject!.id" (updated)="loadData()" (close)="selectedProject=null" *ngIf="selectedProject"></app-project-analysts>
      <app-client-projects [clientId]="projectClient!.id" (updated)="loadData()" (close)="projectClient=null" *ngIf="projectClient"></app-client-projects>
    </div>
  `
})
export class ServiceManagerComponent implements OnInit {
  tab: 'clients' | 'projects' | 'team' = 'clients';
  clients: Client[] = [];
  projects: Project[] = [];
  analysts: User[] = [];

  newClient = '';
  filterClient = 0;
  selectedClient: Client | null = null;
  selectedProject: Project | null = null;
  projectClient: Client | null = null;
  reassignTarget: { [id: number]: number } = {};

  constructor(private clientService: ClientService, private projectService: ProjectService, private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.clientService.getClients().subscribe(cs => this.clients = cs);
    this.projectService.getProjects().subscribe(ps => this.projects = ps);
    this.api.getAnalysts(undefined,1).subscribe(as => this.analysts = as);
  }

  createClient() {
    const name = this.newClient.trim();
    if (!name) return;
    this.clientService.createClient({name}).subscribe({
      next: () => {
        this.newClient='';
        this.loadData();
        alert('Cliente creado');
      },
      error: err => {
        console.error('Error creating client:', err);
        alert('Error al crear cliente');
      }
    });
  }

  openClientAnalysts(c: Client) {
    if (!c.is_active) { alert('Cliente inactivo'); return; }
    this.selectedClient = c;
  }
  openProjectAnalysts(p: Project) {
    if (!p.is_active) { alert('Proyecto inactivo'); return; }
    this.selectedProject = p;
  }
  openProjects(c: Client) {
    if (!c.is_active) { alert('Cliente inactivo'); return; }
    this.projectClient = c;
  }

  filteredProjects(): Project[] {
    return this.filterClient ? this.projects.filter(p => p.client_id === this.filterClient) : this.projects;
  }

  team() {
    const map = new Map<number, {user: User, projects: Project[], load: number}>();
    for (const p of this.projects) {
      for (const a of p.analysts) {
        const entry = map.get(a.id) || {user: a, projects: [], load:0};
        entry.projects.push(p);
        entry.load += p.scripts_per_day || 0;
        map.set(a.id, entry);
      }
    }
    return Array.from(map.values());
  }

  projectNames(projects: Project[]): string {
    return projects.map(p => p.name).join(', ');
  }

  reassign(user: User, projectId: number) {
    if (!projectId) return;
    const current = this.projects.find(p => p.analysts.some(a => a.id===user.id));
    if (!current || current.id === projectId) return;
    this.projectService.unassignAnalyst(current.id, user.id).subscribe(() => {
      this.projectService.assignAnalyst(projectId, user.id).subscribe(() => this.loadData());
    });
  }

  get activeProjects() { return this.projects.filter(p => p.is_active).length; }
  get assignedAnalysts() { const ids = new Set<number>(); this.projects.forEach(p=>p.analysts.forEach(a=>ids.add(a.id))); return ids.size; }
  get teamCapacity() { let sum=0; this.projects.forEach(p=>{ sum += p.scripts_per_day || 0; }); return sum; }
}
