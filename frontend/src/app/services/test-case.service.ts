import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Test, TestCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class TestCaseService {
  constructor(private api: ApiService) {}

  getTestCases(search?: string, priority?: string, status?: string, planId?: number): Observable<Test[]> {
    return this.api.getTests(search, priority, status, planId);
  }

  getTestCase(id: number): Observable<Test> {
    return this.api.getTest(id);
  }

  createTestCase(test: TestCreate): Observable<Test> {
    return this.api.createTest(test);
  }

  updateTestCase(id: number, test: TestCreate): Observable<Test> {
    return this.api.updateTest(id, test);
  }

  deleteTestCase(id: number): Observable<any> {
    return this.api.deleteTest(id);
  }
}
