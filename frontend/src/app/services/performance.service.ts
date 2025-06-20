import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class PerformanceService {
  constructor(private api: ApiService) {}

  downloadK6Script(): Observable<Blob> {
    return this.api.downloadK6Script();
  }
}
