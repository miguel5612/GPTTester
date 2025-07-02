import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Client, Project, ProjectCreate } from '../../models';
import { ClientService } from '../../services/client.service';
import { ProjectService } from '../../services/project.service';

@Component({
  selector: 'app-client-projects',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card" *ngIf="client">
      <div class="card-body">
        <h3 class="card-title">Proyectos de {{ client.name }}</h3>
        <form (ngSubmit)="save()" class="mb-3">
          <div class="input-group mb-2">
            <input class="form-control" placeholder="Nombre del proyecto" [(ngModel)]="form.name" name="name" required>
            <input class="form-control" placeholder="Objetivo" [(ngModel)]="form.objetivo" name="objetivo">
          </div>
          <button class="btn btn-primary me-2" type="submit">{{ editing ? 'Actualizar' : 'Crear' }}</button>
          <button class="btn btn-secondary" type="button" *ngIf="editing" (click)="new()">Cancelar</button>
        </form>
        <ul class="list-group mb-3">
          <li class="list-group-item d-flex justify-content-between align-items-center" *ngFor="let p of projects">
            {{ p.name }}
            <span>
              <button class="btn btn-sm btn-secondary me-2" (click)="edit(p)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(p)">Eliminar</button>
            </span>
          </li>
        </ul>
        <button class="btn btn-secondary" (click)="close.emit()">Cerrar</button>
      </div>
    </div>
  `
})
export class ClientProjectsComponent implements OnChanges {
  @Input() clientId!: number;
  @Output() updated = new EventEmitter<void>();
  @Output() close = new EventEmitter<void>();

  client: Client | null = null;
  projects: Project[] = [];
  editing: Project | null = null;
  form: ProjectCreate = { name: '', client_id: 0, objetivo: '' };

  constructor(
    private clientService: ClientService,
    private projectService: ProjectService
  ) {}

  ngOnChanges() {
    if (this.clientId) {
      this.load();
    }
  }

  load() {
    this.clientService.getClients().subscribe(cs => {
      this.client = cs.find(c => c.id === this.clientId) || null;
    });
    this.projectService.getProjects().subscribe(ps => {
      this.projects = ps.filter(p => p.client_id === this.clientId);
    });
    this.form.client_id = this.clientId;
  }

  new() {
    this.editing = null;
    this.form = { name: '', client_id: this.clientId, objetivo: '' };
  }

  edit(p: Project) {
    this.editing = p;
    this.form = { name: p.name, client_id: this.clientId, objetivo: p.objetivo };
  }

  save() {
    if (!this.form.name.trim()) {
      alert('El nombre es obligatorio');
      return;
    }
    if (!this.client?.is_active) {
      alert('Cliente inactivo');
      return;
    }
    const obs = this.editing
      ? this.projectService.updateProject(this.editing.id, this.form)
      : this.projectService.createProject(this.form);
    obs.subscribe(() => {
      this.load();
      this.editing = null;
      this.form = { name: '', client_id: this.clientId, objetivo: '' };
      this.updated.emit();
    });
  }

  remove(p: Project) {
    if (confirm('¿Eliminar proyecto?')) {
      this.projectService.deleteProject(p.id).subscribe(() => {
        this.load();
        this.updated.emit();
      });
    }
  }
}
