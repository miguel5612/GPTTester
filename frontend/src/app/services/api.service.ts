import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { 
  User, Role, Client, Project, Test, TestPlan, Page, PageElement,
  Action, ActionAssignment, Agent, ExecutionPlan, PlanExecution,
  ExecutionLog, ExecutionSchedule, ExecutionScheduleCreate,
  UserCreate, RoleCreate, ClientCreate, ProjectCreate, TestCreate,
  TestPlanCreate, PageCreate, PageElementCreate, ActionCreate,
  ActionAssignmentCreate, Actor, ActorCreate, AgentCreate, ExecutionPlanCreate,
  LoginRequest, LoginResponse, UserRoleUpdate, PendingExecution,
  MarketplaceComponent, MarketplaceComponentCreate,
  Task, Interaction, Validation, Question, RawData, Feature,
  DigitalAsset, DigitalAssetCreate, Scenario,PagePermission, PagePermissionCreate,
  ApiPermission, ApiPermissionCreate
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
    this.http.post(`${this.baseUrl}/logout`, {}, { headers: this.getHeaders() })
      .subscribe({
        complete: () => {
          this.clearSession();
        },
        error: () => {
          this.clearSession();
        }
      });
  }

  clearSession(): void {
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

  updateRoleActive(id: number, isActive: boolean): Observable<Role> {
    return this.http.put<Role>(`${this.baseUrl}/roles/${id}/active`, { is_active: isActive }, { headers: this.getHeaders() });
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

  updateUserActive(userId: number, isActive: boolean): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/${userId}/active`, { is_active: isActive }, { headers: this.getHeaders() });
  }

  updateUser(id: number, data: any): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/${id}`, data, { headers: this.getHeaders() });
  }

  deleteUser(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${id}`, { headers: this.getHeaders() });
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users/`, { headers: this.getHeaders() });
  }

  getAnalysts(search?: string, page = 1): Observable<User[]> {
    const params: string[] = [];
    if (search) {
      params.push(`search=${encodeURIComponent(search)}`);
    }
    params.push(`skip=${(page - 1) * 10}`);
    params.push('limit=10');
    const query = params.length ? `?${params.join('&')}` : '';
    return this.http.get<User[]>(`${this.baseUrl}/analysts/${query}`, { headers: this.getHeaders() });

  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/${id}`, { headers: this.getHeaders() });
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

  getAssignedClients(): Observable<Client[]> {
    return this.http.get<Client[]>(`${this.baseUrl}/clients/assigned`, { headers: this.getHeaders() });
  }

  assignClientAnalyst(clientId: number, userId: number, dedication?: number): Observable<Client> {
    let url = `${this.baseUrl}/clients/${clientId}/analysts/${userId}`;
    if (dedication !== undefined) {
      url += `?dedication=${dedication}`;
    }
    return this.http.post<Client>(url, {}, { headers: this.getHeaders() });
  }

  unassignClientAnalyst(clientId: number, userId: number): Observable<Client> {
    return this.http.delete<Client>(`${this.baseUrl}/clients/${clientId}/analysts/${userId}`, { headers: this.getHeaders() });
  }

  // Digital Assets
  getDigitalAssets(clientId?: number): Observable<DigitalAsset[]> {
    const query = clientId ? `?clientId=${clientId}` : '';
    return this.http.get<DigitalAsset[]>(`${this.baseUrl}/digitalassets/${query}`, { headers: this.getHeaders() });
  }

  createDigitalAsset(asset: DigitalAssetCreate): Observable<DigitalAsset> {
    return this.http.post<DigitalAsset>(`${this.baseUrl}/digitalassets/`, asset, { headers: this.getHeaders() });
  }

  updateDigitalAsset(id: number, asset: DigitalAssetCreate): Observable<DigitalAsset> {
    return this.http.put<DigitalAsset>(`${this.baseUrl}/digitalassets/${id}`, asset, { headers: this.getHeaders() });
  }

  deleteDigitalAsset(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/digitalassets/${id}`, { headers: this.getHeaders() });
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

  getProjectsByClient(clientId: number): Observable<Project[]> {
    return this.http.get<Project[]>(`${this.baseUrl}/projects/by-client/${clientId}`, { headers: this.getHeaders() });
  }

  assignAnalyst(projectId: number, userId: number, scriptsPerDay?: number): Observable<Project> {
    let url = `${this.baseUrl}/projects/${projectId}/analysts/${userId}`;
    if (scriptsPerDay !== undefined) {
      url += `?scripts_per_day=${scriptsPerDay}`;
    }
    return this.http.post<Project>(url, {}, { headers: this.getHeaders() });
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

  // Role permissions
  getPagePermissions(roleId: number): Observable<PagePermission[]> {
    return this.http.get<PagePermission[]>(`${this.baseUrl}/roles/${roleId}/permissions`, { headers: this.getHeaders() });
  }

  addPagePermission(roleId: number, perm: PagePermissionCreate): Observable<PagePermission> {
    return this.http.post<PagePermission>(`${this.baseUrl}/roles/${roleId}/permissions`, perm, { headers: this.getHeaders() });
  }

  deletePagePermission(roleId: number, page: string): Observable<any> {
    const encoded = encodeURIComponent(page);
    return this.http.delete(`${this.baseUrl}/roles/${roleId}/permissions/${encoded}`, { headers: this.getHeaders() });
  }

  getApiPermissions(roleId: number): Observable<ApiPermission[]> {
    return this.http.get<ApiPermission[]>(`${this.baseUrl}/roles/${roleId}/api-permissions`, { headers: this.getHeaders() });
  }

  addApiPermission(roleId: number, perm: ApiPermissionCreate): Observable<ApiPermission> {
    return this.http.post<ApiPermission>(`${this.baseUrl}/roles/${roleId}/api-permissions`, perm, { headers: this.getHeaders() });
  }

  deleteApiPermission(roleId: number, permId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/roles/${roleId}/api-permissions/${permId}`, { headers: this.getHeaders() });
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

  // Actors
  getActors(clientId?: number): Observable<Actor[]> {
    const query = clientId ? `?client_id=${clientId}` : '';
    return this.http.get<Actor[]>(`${this.baseUrl}/actors/${query}`, { headers: this.getHeaders() });
  }

  createActor(actor: ActorCreate): Observable<Actor> {
    return this.http.post<Actor>(`${this.baseUrl}/actors/`, actor, { headers: this.getHeaders() });
  }

  updateActor(id: number, actor: ActorCreate): Observable<Actor> {
    return this.http.put<Actor>(`${this.baseUrl}/actors/${id}`, actor, { headers: this.getHeaders() });
  }

  deleteActor(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/actors/${id}`, { headers: this.getHeaders() });
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

  runExecutionPlan(id: number, agentId?: number): Observable<PlanExecution> {
    const params = agentId ? `?agent_id=${agentId}` : '';
    return this.http.post<PlanExecution>(`${this.baseUrl}/executionplans/${id}/run${params}`, {}, { headers: this.getHeaders() });
  }

  getPendingExecution(hostname: string): Observable<PendingExecution> {
    return this.http.get<PendingExecution>(`${this.baseUrl}/agents/${hostname}/pending`, { headers: this.getHeaders() });
  }

  getExecutions(planId?: number, agentId?: number): Observable<PlanExecution[]> {
    const params: string[] = [];
    if (planId) params.push(`plan_id=${planId}`);
    if (agentId) params.push(`agent_id=${agentId}`);
    const query = params.length ? `?${params.join('&')}` : '';
    return this.http.get<PlanExecution[]>(`${this.baseUrl}/executions/${query}`, { headers: this.getHeaders() });
  }

  getExecution(id: number): Observable<PlanExecution> {
    return this.http.get<PlanExecution>(`${this.baseUrl}/executions/${id}`, { headers: this.getHeaders() });
  }

  getExecutionLogs(id: number): Observable<ExecutionLog[]> {
    return this.http.get<ExecutionLog[]>(`${this.baseUrl}/executions/${id}/logs`, { headers: this.getHeaders() });
  }

  createSchedule(s: ExecutionScheduleCreate): Observable<ExecutionSchedule> {
    return this.http.post<ExecutionSchedule>(`${this.baseUrl}/schedules/`, s, { headers: this.getHeaders() });
  }

  getSchedules(): Observable<ExecutionSchedule[]> {
    return this.http.get<ExecutionSchedule[]>(`${this.baseUrl}/schedules/`, { headers: this.getHeaders() });
  }

  deleteSchedule(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/schedules/${id}`, { headers: this.getHeaders() });
  }

  downloadExecutionFile(id: number, type: 'report' | 'evidence'): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/executions/${id}/${type}`, {
      headers: this.getHeaders(),
      responseType: 'blob'
    });
  }

  pauseExecution(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/executions/${id}/pause`, {}, { headers: this.getHeaders() });
  }

  resumeExecution(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/executions/${id}/resume`, {}, { headers: this.getHeaders() });
  }

  cancelExecution(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/executions/${id}/cancel`, {}, { headers: this.getHeaders() });
  }

  getDashboardMetrics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/metrics/dashboard`, { headers: this.getHeaders() });
  }

  downloadK6Script(): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/k6/script`, {
      headers: this.getHeaders(),
      responseType: 'blob'
    });
  }

  // Marketplace
  getMarketplaceComponents(): Observable<MarketplaceComponent[]> {
    return this.http.get<MarketplaceComponent[]>(`${this.baseUrl}/marketplace/components/`, { headers: this.getHeaders() });
  }

  createMarketplaceComponent(c: MarketplaceComponentCreate): Observable<MarketplaceComponent> {
    return this.http.post<MarketplaceComponent>(`${this.baseUrl}/marketplace/components/`, c, { headers: this.getHeaders() });
  }

  updateMarketplaceComponent(id: number, c: MarketplaceComponentCreate): Observable<MarketplaceComponent> {
    return this.http.put<MarketplaceComponent>(`${this.baseUrl}/marketplace/components/${id}`, c, { headers: this.getHeaders() });
  }

  deleteMarketplaceComponent(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/marketplace/components/${id}`, { headers: this.getHeaders() });

  }

  // Features
  getFeatures(): Observable<Feature[]> {
    return this.http.get<Feature[]>(`${this.baseUrl}/features/`, { headers: this.getHeaders() });
  }

  createFeature(feature: Feature): Observable<Feature> {
    return this.http.post<Feature>(`${this.baseUrl}/features/`, feature, { headers: this.getHeaders() });
  }

  // Tasks
  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.baseUrl}/tasks/`, { headers: this.getHeaders() });
  }

  createTask(task: Task): Observable<Task> {
    return this.http.post<Task>(`${this.baseUrl}/tasks/`, task, { headers: this.getHeaders() });
  }

  // Interactions
  getInteractions(): Observable<Interaction[]> {
    return this.http.get<Interaction[]>(`${this.baseUrl}/interactions/`, { headers: this.getHeaders() });
  }

  createInteraction(interaction: Interaction): Observable<Interaction> {
    return this.http.post<Interaction>(`${this.baseUrl}/interactions/`, interaction, { headers: this.getHeaders() });
  }

  // Validations
  getValidations(): Observable<Validation[]> {
    return this.http.get<Validation[]>(`${this.baseUrl}/validations/`, { headers: this.getHeaders() });
  }

  createValidation(v: Validation): Observable<Validation> {
    return this.http.post<Validation>(`${this.baseUrl}/validations/`, v, { headers: this.getHeaders() });
  }

  // Questions
  getQuestions(): Observable<Question[]> {
    return this.http.get<Question[]>(`${this.baseUrl}/questions/`, { headers: this.getHeaders() });
  }

  createQuestion(q: Question): Observable<Question> {
    return this.http.post<Question>(`${this.baseUrl}/questions/`, q, { headers: this.getHeaders() });
  }

  // RawData
  getRawData(): Observable<RawData[]> {
    return this.http.get<RawData[]>(`${this.baseUrl}/rawdata/`, { headers: this.getHeaders() });
  }

  createRawData(r: RawData): Observable<RawData> {
    return this.http.post<RawData>(`${this.baseUrl}/rawdata/`, r, { headers: this.getHeaders() });
  }

  // Architect specific endpoints
  getPendingInteractions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/architect/pending/interactions`, { headers: this.getHeaders() });
  }

  getPendingValidations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/architect/pending/validations`, { headers: this.getHeaders() });
  }

  approveInteraction(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/interactionapprovals/${id}/approve`, {}, { headers: this.getHeaders() });
  }

  rejectInteraction(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/interactionapprovals/${id}/reject`, {}, { headers: this.getHeaders() });
  }

  approveValidation(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/validationapprovals/${id}/approve`, {}, { headers: this.getHeaders() });
  }

  rejectValidation(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/validationapprovals/${id}/reject`, {}, { headers: this.getHeaders() });
  }

  // Scenarios
  getScenarios(): Observable<Scenario[]> {
    return this.http.get<Scenario[]>(`${this.baseUrl}/scenarios/`, { headers: this.getHeaders() });
  }

  // Performance execution
  runPerformanceTest(cfg: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/k6/run`, cfg, { headers: this.getHeaders() });
  }

  getPerformanceResults(): Observable<any> {
    return this.http.get(`${this.baseUrl}/k6/results`, { headers: this.getHeaders() });
  }

  isAuthenticated(): boolean {
    return !!this.tokenSubject.value;
  }
}
