import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User, Project } from '../../models';
import { ProjectService } from '../../services/project.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-project-analysts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card" *ngIf="project">
      <div class="card-body">
        <h3 class="card-title">Analistas de {{ project.name }}</h3>
        <div *ngFor="let u of analysts" class="form-check">
          <input class="form-check-input" type="checkbox" [id]="'an-'+u.id"
          [checked]="isAssigned(u)"
          (change)="toggle(u, $any($event.target).checked)">
          <label class="form-check-label" [for]="'an-'+u.id">
            {{ u.username }} ({{ u.role.name }})
          </label>
        </div>
        <button class="btn btn-secondary mt-3" (click)="close.emit()">Cerrar</button>
      </div>
    </div>
  `,
  styles: [`
    .form-check { margin-bottom: 0.5rem; }
  `]
})
export class ProjectAnalystsComponent implements OnChanges {
  @Input() projectId!: number;
  @Output() updated = new EventEmitter<void>();
  @Output() close = new EventEmitter<void>();

  project: Project | null = null;
  analysts: User[] = [];

  constructor(private projectService: ProjectService, private api: ApiService) {}

  ngOnChanges() {
    if (this.projectId) {
      this.load();
    }
  }

  load() {
    this.projectService.getProject(this.projectId).subscribe(p => this.project = p);
    this.api.getUsers().subscribe(users => {
      this.analysts = users.filter(u =>
        u.role.name === 'Analista de Pruebas con skill de automatización' ||
        u.role.name === 'Automatizador de Pruebas'
      );
    });
  }

  isAssigned(u: User): boolean {
    return this.project?.analysts.some(a => a.id === u.id) ?? false;
  }

  toggle(user: User, checked: boolean) {
    if (!this.project) return;
    const obs = checked ?
      this.projectService.assignAnalyst(this.project.id, user.id) :
      this.projectService.unassignAnalyst(this.project.id, user.id);
    obs.subscribe(p => {
      this.project = p;
      this.updated.emit();
    });
  }
}
