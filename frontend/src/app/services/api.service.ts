import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { 
  User, Role, Client, Project, Test, TestPlan, Page, PageElement, 
  Action, ActionAssignment, Agent, ExecutionPlan, PlanExecution,
  UserCreate, RoleCreate, ClientCreate, ProjectCreate, TestCreate,
  TestPlanCreate, PageCreate, PageElementCreate, ActionCreate,
  ActionAssignmentCreate, AgentCreate, ExecutionPlanCreate,
  LoginRequest, LoginResponse, UserRoleUpdate, PendingExecution
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';
  private tokenSubject = new BehaviorSubject<string | null>(localStorage.getItem('token'));
  public token$ = this.tokenSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = this.tokenSubject.value;
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    });
  }

  // Autenticación
  login(credentials: LoginRequest): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return this.http.post<LoginResponse>(`${this.baseUrl}/token`, formData).pipe(
      map(response => {
        localStorage.setItem('token', response.access_token);
        this.tokenSubject.next(response.access_token);
        return response;
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    this.tokenSubject.next(null);
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/me/`, { headers: this.getHeaders() });
  }

  // Roles
  getRoles(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.baseUrl}/roles/`, { headers: this.getHeaders() });
  }

  createRole(role: RoleCreate): Observable<Role> {
    return this.http.post<Role>(`${this.baseUrl}/roles/`, role, { headers: this.getHeaders() });
  }

  updateRole(id: number, role: RoleCreate): Observable<Role> {
    return this.http.put<Role>(`${this.baseUrl}/roles/${id}`, role, { headers: this.getHeaders() });
  }

  deleteRole(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/roles/${id}`, { headers: this.getHeaders() });
  }

  // Usuarios
  createUser(user: UserCreate): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users/`, user, { headers: this.getHeaders() });
  }

  updateUserRole(userId: number, roleUpdate: UserRoleUpdate): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/${userId}/role`, roleUpdate, { headers: this.getHeaders() });
  }

  // Clientes
  getClients(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.baseUrl}/clients/`, { headers: this.getHeaders() });
  }

  createClient(client: ClientCreate): Observable<Client> {
    return this.http.post<Client>(`${this.baseUrl}/clients/`, client, { headers: this.getHeaders() });
  }

  updateClient(id: number, client: ClientCreate): Observable<Client> {
    return this.http.put<Client>(`${this.baseUrl}/clients/${id}`, client, { headers: this.getHeaders() });
  }

  deleteClient(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/clients/${id}`, { headers: this.getHeaders() });
  }

  // Proyectos
  getProjects(): Observable<Project[]> {
    return this.http.get<Project[]>(`${this.baseUrl}/projects/`, { headers: this.getHeaders() });
  }

  getProject(id: number): Observable<Project> {
    return this.http.get<Project>(`${this.baseUrl}/projects/${id}`, { headers: this.getHeaders() });
  }

  createProject(project: ProjectCreate): Observable<Project> {
    return this.http.post<Project>(`${this.baseUrl}/projects/`, project, { headers: this.getHeaders() });
  }

  updateProject(id: number, project: ProjectCreate): Observable<Project> {
    return this.http.put<Project>(`${this.baseUrl}/projects/${id}`, project, { headers: this.getHeaders() });
  }

  deleteProject(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/projects/${id}`, { headers: this.getHeaders() });
  }

  assignAnalyst(projectId: number, userId: number): Observable<Project> {
    return this.http.post<Project>(`${this.baseUrl}/projects/${projectId}/analysts/${userId}`, {}, { headers: this.getHeaders() });
  }

  unassignAnalyst(projectId: number, userId: number): Observable<Project> {
    return this.http.delete<Project>(`${this.baseUrl}/projects/${projectId}/analysts/${userId}`, { headers: this.getHeaders() });
  }

  assignAgentToProject(agentId: number, projectId: number): Observable<Project> {
    return this.http.post<Project>(`${this.baseUrl}/agents/${agentId}/projects/${projectId}`, {}, { headers: this.getHeaders() });
  }

  removeAgentFromProject(agentId: number, projectId: number): Observable<Project> {
    return this.http.delete<Project>(`${this.baseUrl}/agents/${agentId}/projects/${projectId}`, { headers: this.getHeaders() });
  }

  // Tests
  getTests(search?: string, priority?: string, status?: string, planId?: number): Observable<Test[]> {
    const params: string[] = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (priority) params.push(`priority=${priority}`);
    if (status) params.push(`status=${status}`);
    if (planId !== undefined) params.push(`test_plan_id=${planId}`);
    const query = params.length ? `?${params.join('&')}` : '';
    return this.http.get<Test[]>(`${this.baseUrl}/tests/${query}`, { headers: this.getHeaders() });
  }

  getTest(id: number): Observable<Test> {
    return this.http.get<Test>(`${this.baseUrl}/tests/${id}`, { headers: this.getHeaders() });
  }

  createTest(test: TestCreate): Observable<Test> {
    return this.http.post<Test>(`${this.baseUrl}/tests/`, test, { headers: this.getHeaders() });
  }

  updateTest(id: number, test: TestCreate): Observable<Test> {
    return this.http.put<Test>(`${this.baseUrl}/tests/${id}`, test, { headers: this.getHeaders() });
  }

  deleteTest(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/tests/${id}`, { headers: this.getHeaders() });
  }

  // Test Plans
  getTestPlans(): Observable<TestPlan[]> {
    return this.http.get<TestPlan[]>(`${this.baseUrl}/testplans/`, { headers: this.getHeaders() });
  }

  getTestPlan(id: number): Observable<TestPlan> {
    return this.http.get<TestPlan>(`${this.baseUrl}/testplans/${id}`, { headers: this.getHeaders() });
  }

  createTestPlan(testPlan: TestPlanCreate): Observable<TestPlan> {
    return this.http.post<TestPlan>(`${this.baseUrl}/testplans/`, testPlan, { headers: this.getHeaders() });
  }

  updateTestPlan(id: number, testPlan: TestPlanCreate): Observable<TestPlan> {
    return this.http.put<TestPlan>(`${this.baseUrl}/testplans/${id}`, testPlan, { headers: this.getHeaders() });
  }

  deleteTestPlan(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/testplans/${id}`, { headers: this.getHeaders() });
  }

  // Pages
  getPages(): Observable<Page[]> {
    return this.http.get<Page[]>(`${this.baseUrl}/pages/`, { headers: this.getHeaders() });
  }

  getPage(id: number): Observable<Page> {
    return this.http.get<Page>(`${this.baseUrl}/pages/${id}`, { headers: this.getHeaders() });
  }

  createPage(page: PageCreate): Observable<Page> {
    return this.http.post<Page>(`${this.baseUrl}/pages/`, page, { headers: this.getHeaders() });
  }

  updatePage(id: number, page: PageCreate): Observable<Page> {
    return this.http.put<Page>(`${this.baseUrl}/pages/${id}`, page, { headers: this.getHeaders() });
  }

  deletePage(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/pages/${id}`, { headers: this.getHeaders() });
  }

  // Page Elements
  getElements(): Observable<PageElement[]> {
    return this.http.get<PageElement[]>(`${this.baseUrl}/elements/`, { headers: this.getHeaders() });
  }

  getElement(id: number): Observable<PageElement> {
    return this.http.get<PageElement>(`${this.baseUrl}/elements/${id}`, { headers: this.getHeaders() });
  }

  createElement(element: PageElementCreate): Observable<PageElement> {
    return this.http.post<PageElement>(`${this.baseUrl}/elements/`, element, { headers: this.getHeaders() });
  }

  updateElement(id: number, element: PageElementCreate): Observable<PageElement> {
    return this.http.put<PageElement>(`${this.baseUrl}/elements/${id}`, element, { headers: this.getHeaders() });
  }

  deleteElement(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/elements/${id}`, { headers: this.getHeaders() });
  }

  addElementToTest(elementId: number, testId: number): Observable<PageElement> {
    return this.http.post<PageElement>(`${this.baseUrl}/elements/${elementId}/tests/${testId}`, {}, { headers: this.getHeaders() });
  }

  removeElementFromTest(elementId: number, testId: number): Observable<PageElement> {
    return this.http.delete<PageElement>(`${this.baseUrl}/elements/${elementId}/tests/${testId}`, { headers: this.getHeaders() });
  }

  // Actions
  getActions(search?: string, tipo?: string): Observable<Action[]> {
    const params: string[] = [];
    if (search) params.push(`search=${encodeURIComponent(search)}`);
    if (tipo) params.push(`tipo=${tipo}`);
    const query = params.length ? `?${params.join('&')}` : '';
    return this.http.get<Action[]>(`${this.baseUrl}/actions/${query}`, { headers: this.getHeaders() });
  }

  getAction(id: number): Observable<Action> {
    return this.http.get<Action>(`${this.baseUrl}/actions/${id}`, { headers: this.getHeaders() });
  }

  createAction(action: ActionCreate): Observable<Action> {
    return this.http.post<Action>(`${this.baseUrl}/actions/`, action, { headers: this.getHeaders() });
  }

  updateAction(id: number, action: ActionCreate): Observable<Action> {
    return this.http.put<Action>(`${this.baseUrl}/actions/${id}`, action, { headers: this.getHeaders() });
  }

  deleteAction(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/actions/${id}`, { headers: this.getHeaders() });
  }

  // Action Assignments
  getAssignments(): Observable<ActionAssignment[]> {
    return this.http.get<ActionAssignment[]>(`${this.baseUrl}/assignments/`, { headers: this.getHeaders() });
  }

  getAssignment(id: number): Observable<ActionAssignment> {
    return this.http.get<ActionAssignment>(`${this.baseUrl}/assignments/${id}`, { headers: this.getHeaders() });
  }

  createAssignment(assignment: ActionAssignmentCreate): Observable<ActionAssignment> {
    return this.http.post<ActionAssignment>(`${this.baseUrl}/assignments/`, assignment, { headers: this.getHeaders() });
  }

  updateAssignment(id: number, assignment: ActionAssignmentCreate): Observable<ActionAssignment> {
    return this.http.put<ActionAssignment>(`${this.baseUrl}/assignments/${id}`, assignment, { headers: this.getHeaders() });
  }

  deleteAssignment(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/assignments/${id}`, { headers: this.getHeaders() });
  }

  // Agents
  getAgents(): Observable<Agent[]> {
    return this.http.get<Agent[]>(`${this.baseUrl}/agents/`, { headers: this.getHeaders() });
  }

  getAgent(id: number): Observable<Agent> {
    return this.http.get<Agent>(`${this.baseUrl}/agents/${id}`, { headers: this.getHeaders() });
  }

  createAgent(agent: AgentCreate): Observable<Agent> {
    return this.http.post<Agent>(`${this.baseUrl}/agents/`, agent, { headers: this.getHeaders() });
  }

  updateAgent(id: number, agent: AgentCreate): Observable<Agent> {
    return this.http.put<Agent>(`${this.baseUrl}/agents/${id}`, agent, { headers: this.getHeaders() });
  }

  deleteAgent(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/agents/${id}`, { headers: this.getHeaders() });
  }

  // Execution Plans
  getExecutionPlans(agentId?: number, testId?: number, nombre?: string): Observable<ExecutionPlan[]> {
    let params = '';
    const queryParams = [];
    if (agentId) queryParams.push(`agent_id=${agentId}`);
    if (testId) queryParams.push(`test_id=${testId}`);
    if (nombre) queryParams.push(`nombre=${encodeURIComponent(nombre)}`);
    if (queryParams.length > 0) {
      params = '?' + queryParams.join('&');
    }
    
    return this.http.get<ExecutionPlan[]>(`${this.baseUrl}/executionplans/${params}`, { headers: this.getHeaders() });
  }

  getExecutionPlan(id: number): Observable<ExecutionPlan> {
    return this.http.get<ExecutionPlan>(`${this.baseUrl}/executionplans/${id}`, { headers: this.getHeaders() });
  }

  createExecutionPlan(plan: ExecutionPlanCreate): Observable<ExecutionPlan> {
    return this.http.post<ExecutionPlan>(`${this.baseUrl}/executionplans/`, plan, { headers: this.getHeaders() });
  }

  updateExecutionPlan(id: number, plan: ExecutionPlanCreate): Observable<ExecutionPlan> {
    return this.http.put<ExecutionPlan>(`${this.baseUrl}/executionplans/${id}`, plan, { headers: this.getHeaders() });
  }

  deleteExecutionPlan(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/executionplans/${id}`, { headers: this.getHeaders() });
  }

  runExecutionPlan(id: number): Observable<PlanExecution> {
    return this.http.post<PlanExecution>(`${this.baseUrl}/executionplans/${id}/run`, {}, { headers: this.getHeaders() });
  }

  getPendingExecution(hostname: string): Observable<PendingExecution> {
    return this.http.get<PendingExecution>(`${this.baseUrl}/agents/${hostname}/pending`, { headers: this.getHeaders() });
  }

  isAuthenticated(): boolean {
    return !!this.tokenSubject.value;
  }
}
