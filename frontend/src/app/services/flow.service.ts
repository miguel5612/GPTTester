import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface FlowCreate {
  name: string;
  description?: string;
  priority: 'alta' | 'media' | 'baja';
  given: string;
  when: string;
  then: string;
  actor_id: number;
  test_plan_id?: number;
}

export interface FlowResponse {
  id: number;
  name: string;
  description?: string;
  priority: string;
  status: string;
  given: string;
  when: string;
  then: string;
  actor_id: number;
  actor_name?: string;
  test_plan_id?: number;
  created_by: string;
}

export interface ElementMap {
  page_name: string;
  name: string;
  tipo: string;
  estrategia: string;
  valor: string;
  descripcion?: string;
}

export interface ElementResponse {
  id: number;
  name: string;
  page: string;
  tipo: string;
  estrategia: string;
  valor: string;
  descripcion?: string;
}

export interface ActionResponse {
  id: number;
  name: string;
  tipo: string;
  codigo: string;
  argumentos?: string;
}

export interface ActionAssign {
  element_id: number;
  action_id: number;
  parametros?: string;
}

export interface AssignmentResponse {
  id: number;
  action_id: number;
  element_id: number;
  action_name: string;
  element_name: string;
  parametros?: string;
}

export interface FlowDetailResponse extends FlowResponse {
  elements: ElementResponse[];
  actions: ActionResponse[];
  assignments: AssignmentResponse[];
}

export interface AgentInfo {
  id: number;
  alias: string;
  hostname: string;
  os: string;
  categoria?: string;
  online: boolean;
}

export interface ExecutionPlanInfo {
  id: number;
  nombre: string;
  agent_id: number;
}

export interface FlowExecuteInfo {
  flow_id: number;
  flow_name: string;
  available_agents: AgentInfo[];
  execution_plans: ExecutionPlanInfo[];
}

@Injectable({
  providedIn: 'root'
})
export class FlowService {
  private baseUrl = 'http://localhost:8000/api/flows';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    });
  }

  createFlow(flowData: FlowCreate): Observable<FlowResponse> {
    return this.http.post<FlowResponse>(
      `${this.baseUrl}/create`,
      flowData,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        let message = 'Error al crear flujo';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  getMyFlows(status?: string, priority?: string): Observable<FlowResponse[]> {
    const params: string[] = [];
    if (status) params.push(`status=${status}`);
    if (priority) params.push(`priority=${priority}`);
    const query = params.length ? `?${params.join('&')}` : '';
    
    return this.http.get<FlowResponse[]>(
      `${this.baseUrl}/my-flows${query}`,
      { headers: this.getHeaders() }
    );
  }

  getFlowDetail(flowId: number): Observable<FlowDetailResponse> {
    return this.http.get<FlowDetailResponse>(
      `${this.baseUrl}/${flowId}`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        if (error.status === 404) {
          return throwError(() => new Error('Flujo no encontrado'));
        }
        return throwError(() => error);
      })
    );
  }

  mapElement(flowId: number, elementData: ElementMap): Observable<ElementResponse> {
    return this.http.post<ElementResponse>(
      `${this.baseUrl}/${flowId}/map-element`,
      elementData,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        let message = 'Error al mapear elemento';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  assignAction(flowId: number, assignment: ActionAssign): Observable<AssignmentResponse> {
    return this.http.post<AssignmentResponse>(
      `${this.baseUrl}/${flowId}/assign-action`,
      assignment,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        let message = 'Error al asignar acción';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  updateFlowStatus(flowId: number, status: string): Observable<FlowResponse> {
    return this.http.put<FlowResponse>(
      `${this.baseUrl}/${flowId}/status`,
      { status },
      { headers: this.getHeaders() }
    );
  }

  getExecutionInfo(flowId: number): Observable<FlowExecuteInfo> {
    return this.http.get<FlowExecuteInfo>(
      `${this.baseUrl}/${flowId}/execute-info`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(error => {
        let message = 'Error al obtener información de ejecución';
        if (error.error?.detail) {
          message = error.error.detail;
        }
        return throwError(() => new Error(message));
      })
    );
  }

  // Métodos auxiliares
  deleteAssignment(flowId: number, assignmentId: number): Observable<any> {
    // Por ahora usar el API legacy
    return this.http.delete(
      `http://localhost:8000/assignments/${assignmentId}`,
      { headers: this.getHeaders() }
    );
  }

  deleteElement(flowId: number, elementId: number): Observable<any> {
    // Por ahora usar el API legacy
    return this.http.delete(
      `http://localhost:8000/elements/${elementId}/tests/${flowId}`,
      { headers: this.getHeaders() }
    );
  }

  // Obtener acciones disponibles
  getAvailableActions(): Observable<ActionResponse[]> {
    // Por ahora usar el API legacy
    return this.http.get<ActionResponse[]>(
      'http://localhost:8000/actions/',
      { headers: this.getHeaders() }
    );
  }

  // Helpers para estados
  isFlowReady(flow: FlowResponse | FlowDetailResponse): boolean {
    return flow.status === 'listo';
  }

  isFlowNew(flow: FlowResponse | FlowDetailResponse): boolean {
    return flow.status === 'nuevo';
  }

  canExecuteFlow(flow: FlowResponse | FlowDetailResponse): boolean {
    return this.isFlowReady(flow);
  }

  getStatusLabel(status: string): string {
    const labels: { [key: string]: string } = {
      'nuevo': 'Nuevo',
      'mapeando': 'Mapeando elementos',
      'parametrizando': 'Parametrizando',
      'listo': 'Listo para ejecutar'
    };
    return labels[status] || status;
  }

  getStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'nuevo': 'secondary',
      'mapeando': 'warning', 
      'parametrizando': 'info',
      'listo': 'success'
    };
    return colors[status] || 'secondary';
  }

  getPriorityLabel(priority: string): string {
    const labels: { [key: string]: string } = {
      'alta': 'Alta',
      'media': 'Media',
      'baja': 'Baja'
    };
    return labels[priority] || priority;
  }

  getPriorityColor(priority: string): string {
    const colors: { [key: string]: string } = {
      'alta': 'danger',
      'media': 'warning',
      'baja': 'success'
    };
    return colors[priority] || 'secondary';
  }
}
