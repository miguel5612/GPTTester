import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { Project, ProjectCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ProjectService {
  constructor(private api: ApiService) {}

  getProjects(): Observable<Project[]> {
    return this.api.getProjects();
  }

  getProject(id: number): Observable<Project> {
    return this.api.getProject(id);
  }

  getProjectsByClient(clientId: number): Observable<Project[]> {
    return this.api.getProjectsByClient(clientId);
  }

  getProjectsByAsset(assetId: number): Observable<Project[]> {
    return this.api.getProjects().pipe(
      map(ps => ps.filter(p => p.digitalAssetsId === assetId))
    );
  }

  createProject(project: ProjectCreate): Observable<Project> {
    return this.api.createProject(project);
  }

  updateProject(id: number, project: ProjectCreate): Observable<Project> {
    return this.api.updateProject(id, project);
  }

  deleteProject(id: number): Observable<any> {
    return this.api.deleteProject(id);
  }

  assignAnalyst(projectId: number, userId: number, scriptsPerDay?: number): Observable<Project> {
    return this.api.assignAnalyst(projectId, userId, scriptsPerDay);
  }

  unassignAnalyst(projectId: number, userId: number): Observable<Project> {
    return this.api.unassignAnalyst(projectId, userId);
  }
}
