import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { map, tap, catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface ProjectOption {
  id: number;
  name: string;
  objetivo?: string;
}

export interface ClientOption {
  id: number;
  name: string;
  projects: ProjectOption[];
}

export interface WorkspaceOptions {
  clients: ClientOption[];
}

export interface ActorOption {
  id: number;
  name: string;
}

export interface WorkspaceInfo {
  client_id: number;
  client_name: string;
  project_id?: number;
  project_name?: string;
  actors: ActorOption[];
}

export interface WorkspaceSelection {
  client_id: number;
  project_id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class WorkspaceService {
  private baseUrl = 'http://localhost:8000/api/workspace';
  private workspaceSubject = new BehaviorSubject<WorkspaceInfo | null>(null);
  public workspace$ = this.workspaceSubject.asObservable();
  
  private workspaceKey = 'workspace';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {
    // Cargar workspace de localStorage si existe
    const savedWorkspace = localStorage.getItem(this.workspaceKey);
    if (savedWorkspace) {
      try {
        this.workspaceSubject.next(JSON.parse(savedWorkspace));
      } catch (e) {
        localStorage.removeItem(this.workspaceKey);
      }
    }
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    });
  }

  getAvailableWorkspaces(): Observable<WorkspaceOptions> {
    return this.http.get<WorkspaceOptions>(
      `${this.baseUrl}/available`, 
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        console.error('Error al obtener workspaces:', error);
        return throwError(() => error);
      })
    );
  }

  selectWorkspace(selection: WorkspaceSelection): Observable<WorkspaceInfo> {
    return this.http.post<WorkspaceInfo>(
      `${this.baseUrl}/select`,
      selection,
      { headers: this.getHeaders() }
    ).pipe(
      tap(workspace => {
        localStorage.setItem(this.workspaceKey, JSON.stringify(workspace));
        this.workspaceSubject.next(workspace);
      }),
      catchError(error => {
        let message = 'Error al seleccionar workspace';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  getCurrentWorkspace(): Observable<WorkspaceInfo> {
    return this.http.get<WorkspaceInfo>(
      `${this.baseUrl}/current`,
      { headers: this.getHeaders() }
    ).pipe(
      tap(workspace => {
        localStorage.setItem(this.workspaceKey, JSON.stringify(workspace));
        this.workspaceSubject.next(workspace);
      }),
      catchError(error => {
        if (error.status === 404) {
          // No hay workspace seleccionado
          this.clearWorkspace();
          this.router.navigate(['/workspace']);
        }
        return throwError(() => error);
      })
    );
  }

  createActor(name: string): Observable<ActorOption> {
    return this.http.post<ActorOption>(
      `${this.baseUrl}/actors`,
      { name },
      { headers: this.getHeaders() }
    ).pipe(
      tap(() => {
        // Recargar workspace para obtener la lista actualizada de actores
        this.getCurrentWorkspace().subscribe();
      }),
      catchError(error => {
        let message = 'Error al crear actor';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  hasWorkspace(): boolean {
    return !!this.workspaceSubject.value;
  }

  getWorkspaceValue(): WorkspaceInfo | null {
    return this.workspaceSubject.value;
  }

  clearWorkspace(): void {
    localStorage.removeItem(this.workspaceKey);
    this.workspaceSubject.next(null);
  }

  // Métodos de conveniencia
  getCurrentClientId(): number | null {
    return this.workspaceSubject.value?.client_id || null;
  }

  getCurrentProjectId(): number | null {
    return this.workspaceSubject.value?.project_id || null;
  }

  getCurrentActors(): ActorOption[] {
    return this.workspaceSubject.value?.actors || [];
  }

  // Verificar si el usuario necesita seleccionar workspace
  checkWorkspaceRequired(): void {
    if (!this.hasWorkspace() && this.authService.isAuthenticated()) {
      // Intentar cargar workspace actual
      this.getCurrentWorkspace().subscribe({
        error: () => {
          // Si no hay workspace, redirigir a selección
          this.router.navigate(['/workspace']);
        }
      });
    }
  }
}
