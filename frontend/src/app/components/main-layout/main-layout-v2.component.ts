import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { WorkspaceService } from '../../services/workspace-v2.service';

interface MenuItem {
  label: string;
  icon: string;
  route: string;
  roles?: string[];
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="main-layout">
      <!-- Sidebar -->
      <aside class="sidebar" [class.collapsed]="sidebarCollapsed">
        <div class="sidebar-header">
          <div class="logo">
            <i class="fas fa-robot"></i>
            <span *ngIf="!sidebarCollapsed">GPT Tester</span>
          </div>
          <button class="btn-toggle" (click)="toggleSidebar()">
            <i class="fas" [class.fa-chevron-left]="!sidebarCollapsed" [class.fa-chevron-right]="sidebarCollapsed"></i>
          </button>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-section">
            <h3 *ngIf="!sidebarCollapsed">Principal</h3>
            <ul>
              <li *ngFor="let item of getMenuItems()">
                <a 
                  [routerLink]="item.route" 
                  routerLinkActive="active"
                  [title]="item.label">
                  <i [class]="'fas fa-' + item.icon"></i>
                  <span *ngIf="!sidebarCollapsed">{{ item.label }}</span>
                </a>
              </li>
            </ul>
          </div>
        </nav>

        <div class="sidebar-footer">
          <div class="workspace-info" *ngIf="workspace">
            <i class="fas fa-building"></i>
            <div *ngIf="!sidebarCollapsed" class="workspace-details">
              <span class="client">{{ workspace.client_name }}</span>
              <span class="project" *ngIf="workspace.project_name">{{ workspace.project_name }}</span>
            </div>
          </div>
          <button class="btn-change-workspace" (click)="changeWorkspace()" [title]="'Cambiar workspace'">
            <i class="fas fa-exchange-alt"></i>
            <span *ngIf="!sidebarCollapsed">Cambiar</span>
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <div class="main-content">
        <!-- Top bar -->
        <header class="topbar">
          <div class="breadcrumb">
            <span>{{ getCurrentPageTitle() }}</span>
          </div>
          
          <div class="topbar-actions">
            <button class="btn-notifications">
              <i class="fas fa-bell"></i>
              <span class="badge" *ngIf="notifications > 0">{{ notifications }}</span>
            </button>
            
            <div class="user-menu" (click)="toggleUserMenu()">
              <i class="fas fa-user-circle"></i>
              <span>{{ currentUser?.username }}</span>
              <i class="fas fa-chevron-down"></i>
              
              <div class="dropdown-menu" *ngIf="showUserMenu">
                <a (click)="viewProfile()">
                  <i class="fas fa-user"></i> Mi Perfil
                </a>
                <a (click)="viewSettings()">
                  <i class="fas fa-cog"></i> Configuración
                </a>
                <hr>
                <a (click)="logout()">
                  <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                </a>
              </div>
            </div>
          </div>
        </header>

        <!-- Page content -->
        <main class="page-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .main-layout {
      display: flex;
      height: 100vh;
      background: #f5f7fa;
    }

    /* Sidebar Styles */
    .sidebar {
      width: 260px;
      background: white;
      box-shadow: 2px 0 10px rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
      transition: width 0.3s;
      position: relative;
    }

    .sidebar.collapsed {
      width: 70px;
    }

    .sidebar-header {
      padding: 20px;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.25rem;
      font-weight: bold;
      color: #667eea;
    }

    .logo i {
      font-size: 1.5rem;
    }

    .btn-toggle {
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      padding: 5px;
      border-radius: 5px;
      transition: all 0.2s;
    }

    .btn-toggle:hover {
      background: #f5f7fa;
    }

    .sidebar-nav {
      flex: 1;
      padding: 20px 0;
      overflow-y: auto;
    }

    .nav-section {
      margin-bottom: 30px;
    }

    .nav-section h3 {
      padding: 0 20px;
      margin-bottom: 10px;
      font-size: 0.75rem;
      text-transform: uppercase;
      color: #999;
      letter-spacing: 0.5px;
    }

    .sidebar-nav ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .sidebar-nav a {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 12px 20px;
      color: #666;
      text-decoration: none;
      transition: all 0.2s;
      position: relative;
    }

    .sidebar-nav a:hover {
      background: #f5f7fa;
      color: #667eea;
    }

    .sidebar-nav a.active {
      background: #f0f4ff;
      color: #667eea;
      font-weight: 500;
    }

    .sidebar-nav a.active::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: #667eea;
    }

    .sidebar-nav i {
      width: 20px;
      text-align: center;
    }

    .sidebar.collapsed .sidebar-nav a {
      justify-content: center;
    }

    .sidebar-footer {
      padding: 20px;
      border-top: 1px solid #eee;
    }

    .workspace-info {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
      padding: 10px;
      background: #f5f7fa;
      border-radius: 8px;
    }

    .workspace-details {
      flex: 1;
      overflow: hidden;
    }

    .workspace-details span {
      display: block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .workspace-details .client {
      font-weight: 500;
      color: #333;
    }

    .workspace-details .project {
      font-size: 0.875rem;
      color: #666;
    }

    .btn-change-workspace {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      background: white;
      border-radius: 5px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: #666;
      transition: all 0.2s;
    }

    .btn-change-workspace:hover {
      border-color: #667eea;
      color: #667eea;
    }

    /* Main Content Styles */
    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .topbar {
      background: white;
      padding: 0 30px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .breadcrumb {
      font-size: 1.1rem;
      color: #333;
      font-weight: 500;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .btn-notifications {
      background: none;
      border: none;
      color: #666;
      font-size: 1.2rem;
      cursor: pointer;
      position: relative;
      padding: 5px;
    }

    .btn-notifications:hover {
      color: #667eea;
    }

    .badge {
      position: absolute;
      top: 0;
      right: 0;
      background: #ff4757;
      color: white;
      font-size: 0.7rem;
      padding: 2px 5px;
      border-radius: 10px;
    }

    .user-menu {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 8px;
      transition: background 0.2s;
      position: relative;
    }

    .user-menu:hover {
      background: #f5f7fa;
    }

    .user-menu i:first-child {
      font-size: 1.5rem;
      color: #667eea;
    }

    .dropdown-menu {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 5px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 5px 20px rgba(0,0,0,0.15);
      min-width: 200px;
      z-index: 1000;
    }

    .dropdown-menu a {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px 20px;
      color: #333;
      text-decoration: none;
      transition: background 0.2s;
      cursor: pointer;
    }

    .dropdown-menu a:hover {
      background: #f5f7fa;
    }

    .dropdown-menu hr {
      margin: 5px 0;
      border: none;
      border-top: 1px solid #eee;
    }

    .page-content {
      flex: 1;
      overflow-y: auto;
      padding: 30px;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar {
        position: fixed;
        z-index: 100;
        transform: translateX(-100%);
      }

      .sidebar.mobile-open {
        transform: translateX(0);
      }

      .sidebar.collapsed {
        width: 260px;
      }

      .main-content {
        margin-left: 0;
      }
    }
  `]
})
export class MainLayoutComponent implements OnInit {
  sidebarCollapsed = false;
  showUserMenu = false;
  notifications = 0;
  currentUser: any;
  workspace: any;

  menuItems: MenuItem[] = [
    { label: 'Dashboard', icon: 'home', route: '/dashboard' },
    { label: 'Mis Flujos', icon: 'stream', route: '/flows' },
    { label: 'Ejecutar Pruebas', icon: 'play-circle', route: '/execution' },
    { label: 'Reportes', icon: 'chart-bar', route: '/reports' },
    
    // Admin
    { label: 'Usuarios', icon: 'users', route: '/users', roles: ['Administrador'] },
    { label: 'Roles', icon: 'user-shield', route: '/roles', roles: ['Administrador'] },
    { label: 'Agentes', icon: 'server', route: '/agents', roles: ['Administrador'] },
    
    // Gerente
    { label: 'Clientes', icon: 'building', route: '/clients', roles: ['Gerente de servicios'] },
    { label: 'Proyectos', icon: 'folder', route: '/projects', roles: ['Gerente de servicios'] },
    { label: 'Asignaciones', icon: 'users-cog', route: '/assignments', roles: ['Gerente de servicios'] },
    
    // Arquitecto
    { label: 'Componentes', icon: 'puzzle-piece', route: '/marketplace', roles: ['Arquitecto de Automatización'] },
    { label: 'Métricas', icon: 'chart-line', route: '/bi', roles: ['Arquitecto de Automatización', 'Administrador'] },
  ];

  constructor(
    private authService: AuthService,
    private workspaceService: WorkspaceService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.workspaceService.workspace$.subscribe(workspace => {
      this.workspace = workspace;
    });

    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.user-menu')) {
        this.showUserMenu = false;
      }
    });
  }

  getMenuItems(): MenuItem[] {
    const userRole = this.currentUser?.role?.name;
    
    return this.menuItems.filter(item => {
      // Si no tiene roles definidos, es visible para todos
      if (!item.roles) return true;
      
      // Si tiene roles, verificar si el usuario tiene uno de ellos
      return item.roles.includes(userRole);
    });
  }

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  toggleUserMenu() {
    this.showUserMenu = !this.showUserMenu;
  }

  getCurrentPageTitle(): string {
    const route = this.router.url.split('/')[1];
    const item = this.menuItems.find(m => m.route === `/${route}`);
    return item?.label || 'Dashboard';
  }

  changeWorkspace() {
    this.workspaceService.clearWorkspace();
    this.router.navigate(['/workspace']);
  }

  viewProfile() {
    this.showUserMenu = false;
    this.router.navigate(['/profile']);
  }

  viewSettings() {
    this.showUserMenu = false;
    this.router.navigate(['/settings']);
  }

  logout() {
    this.authService.logout();
  }
}
