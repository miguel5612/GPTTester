export interface Role {
  id: number;
  name: string;
  is_active: boolean;
}

export interface User {
  id: number;
  username: string;
  last_login?: string;
  is_active: boolean;
  role: Role;
}

export interface Client {
  id: number;
  name: string;
  is_active: boolean;
  analysts: User[];
  dedication?: number;
}

export interface Project {
  id: number;
  name: string;
  client_id: number;
  is_active: boolean;
  analysts: User[];
  objetivo?: string;
  scripts_per_day?: number;
  test_types?: string;
}

export interface Actor {
  id: number;
  name: string;
  client_id: number;
}

export interface Test {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  actions: Action[];
  priority?: string;
  status?: string;
  given?: string;
  when?: string;
  then?: string;
  test_plan_id?: number;
  actor_id?: number;
}

export interface TestPlan {
  id: number;
  nombre: string;
  objetivo?: string;
  alcance?: string;
  criterios_entrada?: string;
  criterios_salida?: string;
  estrategia?: string;
  responsables?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  historias_bdd?: string;
}

export interface Page {
  id: number;
  name: string;
}

export interface PageElement {
  id: number;
  page_id: number;
  name: string;
  tipo: string;
  estrategia: string;
  valor: string;
  descripcion?: string;
}

export interface Action {
  id: number;
  name: string;
  tipo: string;
  codigo: string;
  argumentos?: string;
}

export interface ActionAssignment {
  id: number;
  action_id: number;
  element_id: number;
  test_id: number;
  parametros?: { [key: string]: string };
}

export interface Agent {
  id: number;
  alias: string;
  hostname: string;
  os: string;
  categoria?: string;
}

export interface ExecutionPlan {
  id: number;
  nombre: string;
  test_id: number;
  agent_id: number;
}

export interface PlanExecution {
  id: number;
  plan_id: number;
  agent_id: number;
  status: string;
  started_at: string;
}

export interface ExecutionLog {
  id: number;
  execution_id: number;
  message: string;
  timestamp: string;
}

export interface ExecutionSchedule {
  id: number;
  plan_id: number;
  run_at: string;
  agent_id?: number;
  executed: boolean;
}

export interface AssignmentDetail {
  action: Action;
  element: PageElement;
  parametros?: { [key: string]: string };
}

export interface PendingExecution {
  execution_id: number;
  plan: ExecutionPlan;
  test: Test;
  assignments: AssignmentDetail[];
}

// DTOs para creación
export interface RoleCreate {
  name: string;
  is_active?: boolean;
}

export interface UserCreate {
  username: string;
  password: string;
}

export interface UserRoleUpdate {
  role_id: number;
}

export interface ClientCreate {
  name: string;
}

export interface ProjectCreate {
  name: string;
  client_id: number;
  objetivo?: string;
}

export interface TestCreate {
  name: string;
  description?: string;
  priority?: string;
  status?: string;
  given?: string;
  when?: string;
  then?: string;
  test_plan_id?: number;
  actor_id?: number;
}

export interface TestPlanCreate {
  nombre: string;
  objetivo?: string;
  alcance?: string;
  criterios_entrada?: string;
  criterios_salida?: string;
  estrategia?: string;
  responsables?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  historias_bdd?: string;
}

export interface PageCreate {
  name: string;
}

export interface PageElementCreate {
  page_id: number;
  name: string;
  tipo: string;
  estrategia: string;
  valor: string;
  descripcion?: string;
}

export interface ActionCreate {
  name: string;
  tipo: string;
  codigo: string;
  argumentos?: string;
}

export interface ActionAssignmentCreate {
  action_id: number;
  element_id: number;
  test_id: number;
  parametros?: { [key: string]: string };
}

export interface ActorCreate {
  name: string;
  client_id: number;
}

export interface AgentCreate {
  alias: string;
  hostname: string;
  os: string;
  categoria?: string;
}

export interface ExecutionPlanCreate {
  nombre: string;
  test_id: number;
  agent_id: number;
}

export interface ExecutionScheduleCreate {
  plan_id: number;
  run_at: string;
  agent_id?: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface MarketplaceComponent {
  id: number;
  name: string;
  description?: string;
  code: string;
  version: string;
  created_at: string;
  updated_at: string;
}

export interface MarketplaceComponentCreate {
  name: string;
  description?: string;
  code: string;
  version?: string;
}

export interface PagePermission {
  id: number;
  page: string;
  role_id: number;
  isStartPage: boolean;
  description?: string;
}

export interface PagePermissionCreate {
  page: string;
  isStartPage?: boolean;
  description?: string;
}

export interface ApiPermission {
  id: number;
  route: string;
  method: string;
  role_id: number;
  description?: string;
}

export interface ApiPermissionCreate {
  route: string;
  method: string;
  description?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
