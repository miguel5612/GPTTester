import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { WorkspaceService, ClientOption, ProjectOption } from '../../services/workspace-v2.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-workspace-selector',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="workspace-container">
      <div class="workspace-header">
        <div class="header-content">
          <h1>Seleccionar Workspace</h1>
          <p>Elige el cliente y proyecto con el que deseas trabajar</p>
        </div>
        <div class="user-info">
          <i class="fas fa-user-circle"></i>
          <span>{{ currentUser?.username }}</span>
          <button class="btn-logout" (click)="logout()">
            <i class="fas fa-sign-out-alt"></i> Salir
          </button>
        </div>
      </div>

      <div class="workspace-content">
        <div class="workspace-card" *ngIf="!loading; else loadingTemplate">
          <form [formGroup]="workspaceForm" (ngSubmit)="onSubmit()">
            
            <!-- Selección de Cliente -->
            <div class="form-section">
              <h3><i class="fas fa-building"></i> Cliente</h3>
              <div class="client-grid">
                <div 
                  class="client-card"
                  *ngFor="let client of clients"
                  [class.selected]="selectedClient?.id === client.id"
                  (click)="selectClient(client)">
                  <div class="client-icon">
                    <i class="fas fa-briefcase"></i>
                  </div>
                  <div class="client-info">
                    <h4>{{ client.name }}</h4>
                    <span class="project-count">{{ client.projects.length }} proyectos</span>
                  </div>
                  <i class="fas fa-check-circle" *ngIf="selectedClient?.id === client.id"></i>
                </div>
              </div>
              <div class="error-message" *ngIf="workspaceForm.get('client_id')?.touched && !selectedClient">
                <i class="fas fa-exclamation-circle"></i>
                Debes seleccionar un cliente
              </div>
            </div>

            <!-- Selección de Proyecto (opcional) -->
            <div class="form-section" *ngIf="selectedClient">
              <h3><i class="fas fa-folder"></i> Proyecto (opcional)</h3>
              <div class="project-grid">
                <div 
                  class="project-card no-project"
                  [class.selected]="!selectedProject"
                  (click)="selectProject(null)">
                  <i class="fas fa-folder-open"></i>
                  <span>Sin proyecto específico</span>
                </div>
                <div 
                  class="project-card"
                  *ngFor="let project of selectedClient.projects"
                  [class.selected]="selectedProject?.id === project.id"
                  (click)="selectProject(project)">
                  <div class="project-header">
                    <h4>{{ project.name }}</h4>
                    <i class="fas fa-check-circle" *ngIf="selectedProject?.id === project.id"></i>
                  </div>
                  <p class="project-objective" *ngIf="project.objetivo">
                    {{ project.objetivo }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Mensaje para usuarios sin clientes asignados -->
            <div class="no-clients-message" *ngIf="clients.length === 0">
              <i class="fas fa-info-circle"></i>
              <h3>No tienes clientes asignados</h3>
              <p>Contacta a tu gerente de servicios para que te asigne a un cliente.</p>
            </div>

            <!-- Errores -->
            <div class="error-message" *ngIf="errorMessage">
              <i class="fas fa-exclamation-circle"></i>
              {{ errorMessage }}
            </div>

            <!-- Botón de continuar -->
            <div class="form-actions" *ngIf="clients.length > 0">
              <button 
                type="submit" 
                class="btn btn-primary"
                [disabled]="!selectedClient || submitting">
                <span *ngIf="!submitting">
                  <i class="fas fa-arrow-right"></i> Continuar
                </span>
                <span *ngIf="submitting">
                  <i class="fas fa-spinner fa-spin"></i> Configurando...
                </span>
              </button>
            </div>
          </form>
        </div>

        <ng-template #loadingTemplate>
          <div class="loading-container">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando workspaces disponibles...</p>
          </div>
        </ng-template>
      </div>
    </div>
  `,
  styles: [`
    .workspace-container {
      min-height: 100vh;
      background: #f5f7fa;
    }

    .workspace-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px 0;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 20px;
    }

    .workspace-header h1 {
      margin: 0;
      font-size: 2rem;
    }

    .workspace-header p {
      margin: 5px 0 0 0;
      opacity: 0.9;
    }

    .user-info {
      position: absolute;
      top: 20px;
      right: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.1);
      padding: 8px 15px;
      border-radius: 25px;
    }

    .btn-logout {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      padding: 5px 10px;
      border-radius: 5px;
      transition: background 0.3s;
    }

    .btn-logout:hover {
      background: rgba(255, 255, 255, 0.2);
    }

    .workspace-content {
      max-width: 1200px;
      margin: 40px auto;
      padding: 0 20px;
    }

    .workspace-card {
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      padding: 40px;
    }

    .form-section {
      margin-bottom: 40px;
    }

    .form-section h3 {
      color: #333;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .form-section h3 i {
      color: #667eea;
    }

    .client-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }

    .client-card {
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      gap: 15px;
      position: relative;
    }

    .client-card:hover {
      border-color: #667eea;
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    .client-card.selected {
      border-color: #667eea;
      background: #f5f7ff;
    }

    .client-icon {
      width: 50px;
      height: 50px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 1.5rem;
    }

    .client-info {
      flex: 1;
    }

    .client-info h4 {
      margin: 0;
      color: #333;
    }

    .project-count {
      font-size: 0.875rem;
      color: #666;
    }

    .client-card .fa-check-circle {
      position: absolute;
      top: 10px;
      right: 10px;
      color: #667eea;
      font-size: 1.2rem;
    }

    .project-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }

    .project-card {
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .project-card:hover {
      border-color: #667eea;
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    .project-card.selected {
      border-color: #667eea;
      background: #f5f7ff;
    }

    .project-card.no-project {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      color: #666;
      border-style: dashed;
    }

    .project-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 10px;
    }

    .project-header h4 {
      margin: 0;
      color: #333;
    }

    .project-header .fa-check-circle {
      color: #667eea;
      font-size: 1.2rem;
    }

    .project-objective {
      margin: 0;
      font-size: 0.875rem;
      color: #666;
      line-height: 1.5;
    }

    .no-clients-message {
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }

    .no-clients-message i {
      font-size: 3rem;
      color: #667eea;
      margin-bottom: 20px;
    }

    .no-clients-message h3 {
      color: #333;
      margin-bottom: 10px;
    }

    .error-message {
      background: #f8d7da;
      color: #721c24;
      padding: 10px 15px;
      border-radius: 5px;
      margin-top: 20px;
      font-size: 0.875rem;
    }

    .error-message i {
      margin-right: 5px;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 40px;
    }

    .btn {
      padding: 12px 30px;
      border: none;
      border-radius: 5px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .loading-container {
      text-align: center;
      padding: 100px 20px;
      color: #666;
    }

    .loading-container i {
      font-size: 3rem;
      color: #667eea;
      margin-bottom: 20px;
    }

    @media (max-width: 768px) {
      .workspace-card {
        padding: 20px;
      }

      .client-grid,
      .project-grid {
        grid-template-columns: 1fr;
      }

      .user-info {
        position: static;
        margin-top: 20px;
        justify-content: center;
      }
    }
  `]
})
export class WorkspaceSelectorComponent implements OnInit {
  workspaceForm: FormGroup;
  clients: ClientOption[] = [];
  selectedClient: ClientOption | null = null;
  selectedProject: ProjectOption | null = null;
  loading = true;
  submitting = false;
  errorMessage = '';
  currentUser: any;

  constructor(
    private fb: FormBuilder,
    private workspaceService: WorkspaceService,
    private authService: AuthService,
    private router: Router
  ) {
    this.workspaceForm = this.fb.group({
      client_id: ['', Validators.required],
      project_id: ['']
    });
  }

  ngOnInit() {
    // Obtener usuario actual
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    // Si ya tiene workspace, redirigir
    if (this.workspaceService.hasWorkspace()) {
      this.router.navigate(['/']);
      return;
    }

    // Cargar workspaces disponibles
    this.loadWorkspaces();
  }

  loadWorkspaces() {
    this.loading = true;
    this.workspaceService.getAvailableWorkspaces().subscribe({
      next: (options) => {
        this.clients = options.clients;
        this.loading = false;
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = 'Error al cargar los clientes disponibles';
        console.error(error);
      }
    });
  }

  selectClient(client: ClientOption) {
    this.selectedClient = client;
    this.selectedProject = null;
    this.workspaceForm.patchValue({
      client_id: client.id,
      project_id: null
    });
  }

  selectProject(project: ProjectOption | null) {
    this.selectedProject = project;
    this.workspaceForm.patchValue({
      project_id: project?.id || null
    });
  }

  onSubmit() {
    if (!this.selectedClient) {
      this.workspaceForm.get('client_id')?.markAsTouched();
      return;
    }

    this.submitting = true;
    this.errorMessage = '';

    const selection = {
      client_id: this.selectedClient.id,
      project_id: this.selectedProject?.id
    };

    this.workspaceService.selectWorkspace(selection).subscribe({
      next: () => {
        // Workspace seleccionado, redirigir al dashboard
        this.router.navigate(['/']);
      },
      error: (error) => {
        this.submitting = false;
        this.errorMessage = error.message || 'Error al seleccionar workspace';
      }
    });
  }

  logout() {
    this.authService.logout();
  }
}
