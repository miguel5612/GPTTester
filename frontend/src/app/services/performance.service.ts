import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Scenario } from '../models';
import { PerformanceConfig } from '../components/performance/performance-config-form.component';

@Injectable({ providedIn: 'root' })
export class PerformanceService {
  constructor(private api: ApiService) {}

  downloadK6Script(): Observable<Blob> {
    return this.api.downloadK6Script();
  }

  getScenarios(): Observable<Scenario[]> {
    return this.api.getScenarios();
  }

  startTest(scenarioId: number, cfg: PerformanceConfig): Observable<any> {
    return this.api.runPerformanceTest({ scenario_id: scenarioId, ...cfg });
  }

  getResults(): Observable<any> {
    return this.api.getPerformanceResults();
  }
}
