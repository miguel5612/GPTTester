import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { WorkspaceService } from './services/workspace.service';

@Injectable()
export class WorkspaceInterceptor implements HttpInterceptor {
  constructor(private workspace: WorkspaceService) {}

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    const headers: Record<string, string> = {};
    if (this.workspace.clientId !== null) {
      headers['X-Client-Id'] = String(this.workspace.clientId);
    }
    if (this.workspace.projectId !== null) {
      headers['X-Project-Id'] = String(this.workspace.projectId);
    }
    const cloned = Object.keys(headers).length
      ? req.clone({ setHeaders: headers })
      : req;
    return next.handle(cloned);
  }
}
