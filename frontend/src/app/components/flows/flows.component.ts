import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FlowService, FlowResponse } from '../../services/flow.service';
import { WorkspaceService } from '../../services/workspace-v2.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-flows',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  template: `
    <div class="flows-container">
      <!-- Header con acciones -->
      <div class="flows-header">
        <div>
          <h2>Mis Flujos de Prueba</h2>
          <p>Gestiona tus escenarios de automatización</p>
        </div>
        <button class="btn btn-primary" (click)="showCreateModal = true">
          <i class="fas fa-plus"></i> Nuevo Flujo
        </button>
      </div>

      <!-- Filtros -->
      <div class="filters-bar">
        <div class="filter-group">
          <label>Estado:</label>
          <select [(ngModel)]="statusFilter" (change)="loadFlows()">
            <option value="">Todos</option>
            <option value="nuevo">Nuevos</option>
            <option value="mapeando">Mapeando</option>
            <option value="parametrizando">Parametrizando</option>
            <option value="listo">Listos</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Prioridad:</label>
          <select [(ngModel)]="priorityFilter" (change)="loadFlows()">
            <option value="">Todas</option>
            <option value="alta">Alta</option>
            <option value="media">Media</option>
            <option value="baja">Baja</option>
          </select>
        </div>
        <div class="stats">
          <span><i class="fas fa-chart-line"></i> {{ flows.length }} flujos totales</span>
          <span><i class="fas fa-check-circle"></i> {{ readyFlows }} listos</span>
        </div>
      </div>

      <!-- Lista de flujos -->
      <div class="flows-grid" *ngIf="!loading; else loadingTemplate">
        <div class="flow-card" *ngFor="let flow of flows" (click)="navigateToFlow(flow)">
          <div class="flow-header">
            <h3>{{ flow.name }}</h3>
            <span class="flow-status" [class]="getStatusClass(flow.status)">
              {{ flowService.getStatusLabel(flow.status) }}
            </span>
          </div>
          
          <div class="flow-description" *ngIf="flow.description">
            {{ flow.description }}
          </div>

          <div class="flow-scenario">
            <div class="scenario-step">
              <strong>Dado:</strong> {{ flow.given }}
            </div>
            <div class="scenario-step">
              <strong>Cuando:</strong> {{ flow.when }}
            </div>
            <div class="scenario-step">
              <strong>Entonces:</strong> {{ flow.then }}
            </div>
          </div>

          <div class="flow-footer">
            <span class="flow-priority" [class]="getPriorityClass(flow.priority)">
              <i class="fas fa-flag"></i> {{ flowService.getPriorityLabel(flow.priority) }}
            </span>
            <span class="flow-actor">
              <i class="fas fa-user"></i> {{ flow.actor_name }}
            </span>
            <span class="flow-author">
              <i class="fas fa-clock"></i> {{ flow.created_by }}
            </span>
          </div>

          <div class="flow-actions" (click)="$event.stopPropagation()">
            <button 
              class="btn-icon" 
              title="Editar"
              (click)="editFlow(flow)"
              *ngIf="flow.status === 'nuevo'">
              <i class="fas fa-edit"></i>
            </button>
            <button 
              class="btn-icon" 
              title="Mapear elementos"
              (click)="navigateToMapping(flow)"
              *ngIf="canMap(flow)">
              <i class="fas fa-map-marked-alt"></i>
            </button>
            <button 
              class="btn-icon" 
              title="Ejecutar"
              (click)="navigateToExecution(flow)"
              *ngIf="flowService.canExecuteFlow(flow)">
              <i class="fas fa-play"></i>
            </button>
          </div>
        </div>

        <div class="empty-state" *ngIf="flows.length === 0">
          <i class="fas fa-folder-open"></i>
          <h3>No hay flujos</h3>
          <p>Crea tu primer flujo de prueba para comenzar</p>
        </div>
      </div>

      <ng-template #loadingTemplate>
        <div class="loading-container">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Cargando flujos...</p>
        </div>
      </ng-template>

      <!-- Modal de creación -->
      <div class="modal" *ngIf="showCreateModal" (click)="closeModal($event)">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3>Crear Nuevo Flujo</h3>
            <button class="btn-close" (click)="showCreateModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form [formGroup]="createForm" (ngSubmit)="createFlow()">
            <div class="form-group">
              <label>Nombre del flujo *</label>
              <input 
                type="text" 
                class="form-control"
                formControlName="name"
                placeholder="Ej: Login exitoso en aplicación">
              <div class="field-error" *ngIf="isFieldInvalid('name')">
                El nombre es requerido (mínimo 3 caracteres)
              </div>
            </div>

            <div class="form-group">
              <label>Descripción</label>
              <textarea 
                class="form-control"
                formControlName="description"
                rows="2"
                placeholder="Describe brevemente el propósito del flujo">
              </textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Prioridad</label>
                <select class="form-control" formControlName="priority">
                  <option value="alta">Alta</option>
                  <option value="media">Media</option>
                  <option value="baja">Baja</option>
                </select>
              </div>

              <div class="form-group">
                <label>Actor *</label>
                <select class="form-control" formControlName="actor_id">
                  <option value="">Selecciona un actor</option>
                  <option *ngFor="let actor of actors" [value]="actor.id">
                    {{ actor.name }}
                  </option>
                </select>
                <div class="field-error" *ngIf="isFieldInvalid('actor_id')">
                  Debes seleccionar un actor
                </div>
              </div>
            </div>

            <div class="scenario-section">
              <h4>Escenario BDD</h4>
              
              <div class="form-group">
                <label>Dado (contexto inicial) *</label>
                <textarea 
                  class="form-control"
                  formControlName="given"
                  rows="2"
                  placeholder="Ej: que estoy en la página de login">
                </textarea>
                <div class="field-error" *ngIf="isFieldInvalid('given')">
                  El contexto inicial es requerido
                </div>
              </div>

              <div class="form-group">
                <label>Cuando (acción) *</label>
                <textarea 
                  class="form-control"
                  formControlName="when"
                  rows="2"
                  placeholder="Ej: ingreso credenciales válidas y hago clic en iniciar sesión">
                </textarea>
                <div class="field-error" *ngIf="isFieldInvalid('when')">
                  La acción es requerida
                </div>
              </div>

              <div class="form-group">
                <label>Entonces (resultado esperado) *</label>
                <textarea 
                  class="form-control"
                  formControlName="then"
                  rows="2"
                  placeholder="Ej: debo ver el dashboard principal">
                </textarea>
                <div class="field-error" *ngIf="isFieldInvalid('then')">
                  El resultado esperado es requerido
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" (click)="showCreateModal = false">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="creating">
                <span *ngIf="!creating">Crear Flujo</span>
                <span *ngIf="creating">
                  <i class="fas fa-spinner fa-spin"></i> Creando...
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .flows-container {
      padding: 20px;
    }

    .flows-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
    }

    .flows-header h2 {
      margin: 0;
      color: #333;
    }

    .flows-header p {
      margin: 5px 0 0 0;
      color: #666;
    }

    .filters-bar {
      background: white;
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
      display: flex;
      gap: 20px;
      align-items: center;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .filter-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .filter-group label {
      color: #666;
      font-weight: 500;
    }

    .filter-group select {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 5px;
      background: white;
    }

    .stats {
      margin-left: auto;
      display: flex;
      gap: 20px;
      color: #666;
    }

    .stats span {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .flows-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
    }

    .flow-card {
      background: white;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
      cursor: pointer;
      transition: all 0.3s;
      position: relative;
    }

    .flow-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    .flow-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 15px;
    }

    .flow-header h3 {
      margin: 0;
      color: #333;
      font-size: 1.1rem;
      flex: 1;
    }

    .flow-status {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 500;
      text-transform: uppercase;
    }

    .flow-status.status-nuevo {
      background: #e3f2fd;
      color: #1976d2;
    }

    .flow-status.status-mapeando {
      background: #fff3e0;
      color: #f57c00;
    }

    .flow-status.status-parametrizando {
      background: #f3e5f5;
      color: #7b1fa2;
    }

    .flow-status.status-listo {
      background: #e8f5e9;
      color: #388e3c;
    }

    .flow-description {
      color: #666;
      font-size: 0.875rem;
      margin-bottom: 15px;
    }

    .flow-scenario {
      background: #f5f7fa;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 15px;
    }

    .scenario-step {
      font-size: 0.875rem;
      color: #555;
      margin-bottom: 8px;
      line-height: 1.4;
    }

    .scenario-step:last-child {
      margin-bottom: 0;
    }

    .scenario-step strong {
      color: #333;
    }

    .flow-footer {
      display: flex;
      gap: 15px;
      font-size: 0.8rem;
      color: #666;
    }

    .flow-footer span {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .flow-priority.priority-alta {
      color: #d32f2f;
    }

    .flow-priority.priority-media {
      color: #f57c00;
    }

    .flow-priority.priority-baja {
      color: #388e3c;
    }

    .flow-actions {
      position: absolute;
      top: 20px;
      right: 20px;
      display: flex;
      gap: 5px;
      opacity: 0;
      transition: opacity 0.3s;
    }

    .flow-card:hover .flow-actions {
      opacity: 1;
    }

    .btn-icon {
      width: 32px;
      height: 32px;
      border: none;
      background: #f5f7fa;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .btn-icon:hover {
      background: #667eea;
      color: white;
    }

    .empty-state {
      text-align: center;
      padding: 80px 20px;
      color: #666;
    }

    .empty-state i {
      font-size: 4rem;
      color: #ddd;
      margin-bottom: 20px;
    }

    .loading-container {
      text-align: center;
      padding: 80px 20px;
      color: #666;
    }

    .loading-container i {
      font-size: 3rem;
      color: #667eea;
    }

    /* Modal styles */
    .modal {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal-content {
      background: white;
      border-radius: 10px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      border-bottom: 1px solid #eee;
    }

    .modal-header h3 {
      margin: 0;
      color: #333;
    }

    .btn-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      color: #666;
      cursor: pointer;
    }

    .modal-content form {
      padding: 20px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      margin-bottom: 5px;
      color: #333;
      font-weight: 500;
    }

    .form-control {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 5px;
      font-size: 14px;
    }

    .form-control:focus {
      outline: none;
      border-color: #667eea;
    }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .field-error {
      color: #d32f2f;
      font-size: 0.875rem;
      margin-top: 5px;
    }

    .scenario-section {
      margin-top: 30px;
    }

    .scenario-section h4 {
      color: #333;
      margin-bottom: 15px;
    }

    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding: 20px;
      border-top: 1px solid #eee;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
    }

    .btn-primary {
      background: #667eea;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background: #5a67d8;
    }

    .btn-secondary {
      background: #e0e0e0;
      color: #333;
    }

    .btn-secondary:hover {
      background: #d0d0d0;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    @media (max-width: 768px) {
      .flows-grid {
        grid-template-columns: 1fr;
      }

      .filters-bar {
        flex-direction: column;
        align-items: stretch;
      }

      .stats {
        margin-left: 0;
        margin-top: 10px;
      }

      .form-row {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class FlowsComponent implements OnInit {
  flows: FlowResponse[] = [];
  loading = true;
  showCreateModal = false;
  creating = false;
  
  statusFilter = '';
  priorityFilter = '';
  
  createForm: FormGroup;
  actors: any[] = [];

  constructor(
    private fb: FormBuilder,
    public flowService: FlowService,
    private workspaceService: WorkspaceService,
    private authService: AuthService,
    private router: Router
  ) {
    this.createForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: [''],
      priority: ['media'],
      actor_id: ['', Validators.required],
      given: ['', Validators.required],
      when: ['', Validators.required],
      then: ['', Validators.required],
      test_plan_id: [null]
    });
  }

  ngOnInit() {
    this.loadFlows();
    this.loadActors();
  }

  loadFlows() {
    this.loading = true;
    this.flowService.getMyFlows(this.statusFilter, this.priorityFilter).subscribe({
      next: (flows) => {
        this.flows = flows;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar flujos:', error);
        this.loading = false;
      }
    });
  }

  loadActors() {
    this.workspaceService.workspace$.subscribe(workspace => {
      if (workspace) {
        this.actors = workspace.actors;
      }
    });
  }

  get readyFlows(): number {
    return this.flows.filter(f => f.status === 'listo').length;
  }

  getStatusClass(status: string): string {
    return `status-${status}`;
  }

  getPriorityClass(priority: string): string {
    return `priority-${priority}`;
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.createForm.get(fieldName);
    return !!(field && field.invalid && field.touched);
  }

  canMap(flow: FlowResponse): boolean {
    return ['nuevo', 'mapeando', 'parametrizando'].includes(flow.status);
  }

  createFlow() {
    if (this.createForm.invalid) {
      Object.keys(this.createForm.controls).forEach(key => {
        this.createForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.creating = true;
    this.flowService.createFlow(this.createForm.value).subscribe({
      next: (flow) => {
        this.showCreateModal = false;
        this.createForm.reset({ priority: 'media' });
        this.loadFlows();
        // Navegar al flujo creado para mapear elementos
        this.navigateToMapping(flow);
      },
      error: (error) => {
        console.error('Error al crear flujo:', error);
        this.creating = false;
      }
    });
  }

  editFlow(flow: FlowResponse) {
    // TODO: Implementar edición
    console.log('Editar flujo:', flow);
  }

  navigateToFlow(flow: FlowResponse) {
    this.router.navigate(['/flow-detail', flow.id]);
  }

  navigateToMapping(flow: FlowResponse) {
    this.router.navigate(['/flow-mapping', flow.id]);
  }

  navigateToExecution(flow: FlowResponse) {
    this.router.navigate(['/flow-execution', flow.id]);
  }

  closeModal(event: Event) {
    if (event.target === event.currentTarget) {
      this.showCreateModal = false;
    }
  }
}
