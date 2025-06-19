import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class MonitorService {
  private baseWs = 'ws://localhost:8000/ws/execution';

  constructor(private api: ApiService) {}

  connect(executionId: number): WebSocketSubject<any> {
    const token = localStorage.getItem('token');
    const url = `${this.baseWs}/${executionId}?token=${token}`;
    return webSocket(url);
  }

  pause(id: number) { return this.api.pauseExecution(id); }
  resume(id: number) { return this.api.resumeExecution(id); }
  cancel(id: number) { return this.api.cancelExecution(id); }
}
