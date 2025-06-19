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
        <input class="form-control mb-2" placeholder="Buscar..." [(ngModel)]="search" (ngModelChange)="onSearch()" />
        <div *ngFor="let u of analysts" class="form-check">
          <input class="form-check-input" type="checkbox" [id]="'an-'+u.id"
            [checked]="isAssigned(u)"
            (change)="toggle(u, $any($event.target).checked)">
          <label class="form-check-label" [for]="'an-'+u.id">
            {{ u.username }} ({{ u.role.name }})
          </label>
        </div>
        <nav class="mt-2">
          <ul class="pagination mb-0">
            <li class="page-item" [class.disabled]="page === 1">
              <button class="page-link" (click)="prev()">Anterior</button>
            </li>
            <li class="page-item"><span class="page-link">{{ page }}</span></li>
            <li class="page-item" [class.disabled]="analysts.length < 10">
              <button class="page-link" (click)="next()" [disabled]="analysts.length < 10">Siguiente</button>
            </li>
          </ul>
        </nav>
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
  page = 1;
  search = '';

  constructor(private projectService: ProjectService, private api: ApiService) {}

  ngOnChanges() {
    if (this.projectId) {
      this.load();
    }
  }

  load() {
    this.projectService.getProject(this.projectId).subscribe(p => this.project = p);
    this.api.getAnalysts(this.search, this.page).subscribe(users => {
      this.analysts = users;
    });
  }

  onSearch() {
    this.page = 1;
    this.load();
  }

  prev() {
    if (this.page > 1) {
      this.page--;
      this.load();
    }
  }

  next() {
    if (this.analysts.length === 10) {
      this.page++;
      this.load();
    }
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
