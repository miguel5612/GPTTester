import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ExecutionPlan, PlanExecution, ExecutionLog, ExecutionSchedule, ExecutionScheduleCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ExecutionService {
  constructor(private api: ApiService) {}

  getPlans(): Observable<ExecutionPlan[]> {
    return this.api.getExecutionPlans();
  }

  runPlan(id: number, agentId?: number): Observable<PlanExecution> {
    return this.api.runExecutionPlan(id, agentId);
  }

  getExecutions(planId?: number, agentId?: number): Observable<PlanExecution[]> {
    return this.api.getExecutions(planId, agentId);
  }

  getExecution(id: number): Observable<PlanExecution> {
    return this.api.getExecution(id);
  }

  getExecutionLogs(id: number): Observable<ExecutionLog[]> {
    return this.api.getExecutionLogs(id);
  }

  createSchedule(s: ExecutionScheduleCreate): Observable<ExecutionSchedule> {
    return this.api.createSchedule(s);
  }

  getSchedules(): Observable<ExecutionSchedule[]> {
    return this.api.getSchedules();
  }

  deleteSchedule(id: number): Observable<any> {
    return this.api.deleteSchedule(id);
  }

  downloadReport(id: number, type: 'report' | 'evidence'): Observable<Blob> {
    return this.api.downloadExecutionFile(id, type);
  }
}
