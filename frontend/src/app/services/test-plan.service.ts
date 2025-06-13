import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { TestPlan, TestPlanCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class TestPlanService {
  constructor(private api: ApiService) {}

  getTestPlans(): Observable<TestPlan[]> {
    return this.api.getTestPlans();
  }

  getTestPlan(id: number): Observable<TestPlan> {
    return this.api.getTestPlan(id);
  }

  createTestPlan(plan: TestPlanCreate): Observable<TestPlan> {
    return this.api.createTestPlan(plan);
  }

  updateTestPlan(id: number, plan: TestPlanCreate): Observable<TestPlan> {
    return this.api.updateTestPlan(id, plan);
  }

  deleteTestPlan(id: number): Observable<any> {
    return this.api.deleteTestPlan(id);
  }
}
