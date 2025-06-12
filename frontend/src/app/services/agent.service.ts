import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { Agent, AgentCreate, Project } from '../models';

@Injectable({ providedIn: 'root' })
export class AgentService {
  constructor(private api: ApiService) {}

  getAgents(): Observable<Agent[]> {
    return this.api.getAgents();
  }

  getAgent(id: number): Observable<Agent> {
    return this.api.getAgent(id);
  }

  createAgent(agent: AgentCreate): Observable<Agent> {
    return this.api.createAgent(agent);
  }

  updateAgent(id: number, agent: AgentCreate): Observable<Agent> {
    return this.api.updateAgent(id, agent);
  }

  deleteAgent(id: number): Observable<any> {
    return this.api.deleteAgent(id);
  }

  assignToProject(agentId: number, projectId: number): Observable<Project> {
    return this.api.assignAgentToProject(agentId, projectId);
  }

  removeFromProject(agentId: number, projectId: number): Observable<Project> {
    return this.api.removeAgentFromProject(agentId, projectId);
  }

  checkHostname(hostname: string, ignoreId?: number): Observable<boolean> {
    return this.getAgents().pipe(
      map(list => list.some(a => a.hostname === hostname && a.id !== ignoreId))
    );
  }
}
