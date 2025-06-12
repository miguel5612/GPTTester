import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ExecutionPlan, PlanExecution } from '../models';

@Injectable({ providedIn: 'root' })
export class ExecutionService {
  constructor(private api: ApiService) {}

  getPlans(): Observable<ExecutionPlan[]> {
    return this.api.getExecutionPlans();
  }

  runPlan(id: number): Observable<PlanExecution> {
    return this.api.runExecutionPlan(id);
  }

  getExecutions(planId?: number, agentId?: number): Observable<PlanExecution[]> {
    return this.api.getExecutions(planId, agentId);
  }

  getExecution(id: number): Observable<PlanExecution> {
    return this.api.getExecution(id);
  }

  downloadReport(id: number, type: 'report' | 'evidence'): Observable<Blob> {
    return this.api.downloadExecutionFile(id, type);
  }
}
