import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Client, Project } from '../../models';
import { ClientService } from '../../services/client.service';
import { ProjectService } from '../../services/project.service';
import { WorkspaceService } from '../../services/workspace.service';

@Component({
  selector: 'app-workspace-selector',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatSelectModule,
    MatFormFieldModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="workspace-container" *ngIf="!isLoading; else loading">
      <h2>Seleccionar Workspace</h2>
      <mat-form-field appearance="fill" class="w-100">
        <mat-label>Cliente</mat-label>
        <mat-select [(ngModel)]="selectedClient" (selectionChange)="onClientSelect()">
          <mat-option *ngFor="let c of clients" [value]="c">
            {{ c.name }}<span *ngIf="c.dedication"> - {{ c.dedication }}%</span>
          </mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="fill" class="w-100" *ngIf="selectedClient">
        <mat-label>Proyecto</mat-label>
        <mat-select [(ngModel)]="selectedProject" (selectionChange)="onProjectSelect()">
          <mat-option *ngFor="let p of projects" [value]="p">
            {{ p.name }}<span *ngIf="p.scripts_per_day"> - {{ p.scripts_per_day }} scripts/día</span>
          </mat-option>
        </mat-select>
      </mat-form-field>
    </div>
    <ng-template #loading>
      <div class="loading">
        <mat-progress-spinner mode="indeterminate"></mat-progress-spinner>
      </div>
    </ng-template>
  `,
  styles: [`
    .workspace-container {
      max-width: 400px;
      margin: 2rem auto;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
    }
  `]
})
export class WorkspaceSelectorComponent implements OnInit {
  clients: Client[] = [];
  projects: Project[] = [];
  selectedClient: Client | null = null;
  selectedProject: Project | null = null;
  isLoading = true;

  constructor(
    private clientService: ClientService,
    private projectService: ProjectService,
    private workspace: WorkspaceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.clientService.getAssignedClients().subscribe({
      next: clients => {
        this.clients = clients;
        if (clients.length === 1) {
          this.selectedClient = clients[0];
          this.loadProjects();
        } else {
          this.isLoading = false;
        }
      },
      error: () => (this.isLoading = false)
    });
  }

  onClientSelect(): void {
    this.selectedProject = null;
    this.loadProjects();
  }

  loadProjects(): void {
    if (!this.selectedClient) {
      return;
    }
    this.isLoading = true;
    this.projectService.getProjectsByClient(this.selectedClient.id).subscribe({
      next: projects => {
        this.projects = projects;
        if (projects.length === 1) {
          this.selectedProject = projects[0];
          this.saveWorkspace();
        } else {
          this.isLoading = false;
        }
      },
      error: () => (this.isLoading = false)
    });
  }

  onProjectSelect(): void {
    this.saveWorkspace();
  }

  saveWorkspace(): void {
    if (this.selectedClient && this.selectedProject) {
      this.workspace.setWorkspace(this.selectedClient.id, this.selectedProject.id);
      this.router.navigate(['/dashboard']);
    }
  }
}
