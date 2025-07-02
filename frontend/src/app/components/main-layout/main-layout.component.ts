import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { User, Client, Project } from '../../models';

interface MenuItem {
  label: string;
  route?: string;
  icon: string;
  children?: { label: string; route: string; icon: string }[];
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="layout-container" [class.sidebar-open]="sidebarOpen">
      <header class="header">
        <button class="hamburger" (click)="toggleSidebar()">☰</button>
        <div class="logo">{{ headerTitle }}</div>
        <div class="user-info" *ngIf="currentUser">
          <span class="user-name">{{ currentUser.username }}</span>
          <button class="btn-logout" (click)="logout()">Salir</button>
        </div>
      </header>

      <div class="layout-grid">
        <nav class="sidebar" [class.mobile-hidden]="!sidebarOpen && isMobile">
          <ul>
            <li *ngFor="let item of menu">
              <a [routerLink]="item.route" routerLinkActive="active" (click)="onNavigate()">
                <span class="icon">{{ item.icon }}</span>
                <span class="label">{{ item.label }}</span>
              </a>
            </li>
            <li *ngFor="let c of clients">
              <details>
                <summary>
                  <span class="icon">📁</span>
                  <span class="label">{{ c.name }}</span>
                </summary>
                <ul>
                  <li>
                    <a [routerLink]="'/clients/' + c.id + '/actors'" routerLinkActive="active" (click)="onNavigate()">
                      <span class="icon">🎭</span>
                      <span class="label">Actores</span>
                    </a>
                  </li>
                  <li *ngFor="let p of projectsByClient[c.id] || []">
                    <details>
                      <summary>
                        <span class="icon">📂</span>
                        <span class="label">{{ p.name }}</span>
                      </summary>
                      <ul>
                        <li>
                          <a [routerLink]="'/projects/' + p.id + '/scenarios'" routerLinkActive="active" (click)="onNavigate()">
                            <span class="icon">📜</span>
                            <span class="label">Escenarios</span>
                          </a>
                        </li>
                        <li>
                          <a [routerLink]="'/projects/' + p.id + '/features'" routerLinkActive="active" (click)="onNavigate()">
                            <span class="icon">🌟</span>
                            <span class="label">Features</span>
                          </a>
                        </li>
                      </ul>
                    </details>
                  </li>
                </ul>
              </details>
            </li>
          </ul>
        </nav>
        <main class="content">
          <router-outlet></router-outlet>
        </main>
      </div>

      <footer class="footer">
        © 2024 GPTTester
      </footer>
    </div>
  `,
  styles: [`
    .layout-container { display: flex; flex-direction: column; min-height: 100vh; }
    .header { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 1rem; background: var(--panel-bg); border-bottom: 1px solid var(--border-color); position: relative; }
    .hamburger { background: none; border: none; font-size: 1.5rem; margin-right: 1rem; display: none; }
    .logo { font-weight: 600; }
    .chip { background: var(--bg-general-alt); border-radius: 12px; padding: 0.25rem 0.75rem; font-size: 0.75rem; }
    .user-info { display: flex; align-items: center; gap: 0.5rem; }
    .btn-logout { background: var(--btn-primary); color: var(--btn-primary-text); border: none; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; }
    .layout-grid { display: flex; flex: 1; }
    .sidebar { width: 200px; background: var(--panel-bg); border-right: 1px solid var(--border-color); }
    .sidebar ul { list-style: none; margin: 0; padding: 0; }
    .sidebar li a { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; text-decoration: none; color: var(--title-color); }
    .sidebar li a.active { background: var(--btn-primary); color: var(--btn-primary-text); }
    .sidebar details { border-bottom: 1px solid var(--border-color); }
    .sidebar details summary { cursor: pointer; padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.5rem; list-style: none; }
    .sidebar details ul { list-style: none; margin: 0; padding: 0; }
    .sidebar details ul li a { padding-left: 2rem; }
    .content { flex: 1; padding: 1rem; }
    .footer { text-align: center; padding: 0.5rem; background: var(--panel-bg); border-top: 1px solid var(--border-color); }

    @media (max-width: 768px) {
      .hamburger { display: block; }
      .sidebar { position: absolute; left: 0; top: 0; bottom: 0; transform: translateX(-100%); transition: transform 0.3s ease; z-index: 1000; }
      .sidebar.mobile-hidden { transform: translateX(-100%); }
      .layout-container.sidebar-open .sidebar { transform: translateX(0); }
    }
  `]
})
export class MainLayoutComponent implements OnInit {
  currentUser: User | null = null;
  menu: MenuItem[] = [];
  clients: Client[] = [];
  projectsByClient: { [key: number]: Project[] } = {};
  sidebarOpen = false;
  headerTitle = 'GPTTester';

  constructor(
    private api: ApiService,
    private router: Router
  ) {}

  buildMenu() {
    const base = [
      { label: 'Clientes', route: '/clients', icon: '🏢' }
    ];
    const extra = [
      { label: 'Interacciones', route: '/interactions', icon: '⚙️' }
    ];
    const admin = [
      { label: 'Dashboard', route: '/dashboard', icon: '🏠' },
      { label: 'Usuarios', route: '/users', icon: '👥' },
      { label: 'Roles', route: '/roles', icon: '🛡️' },
      { label: 'Permisos', route: '/permissions', icon: '🔑' },
      { label: 'Agentes', route: '/agents', icon: '🤖' }
    ];
    const perf = { label: 'Performance', route: '/performance', icon: '🚀' };

    if (this.currentUser?.role?.name === 'Administrador') {
      this.menu = [...admin, perf, ...base, ...extra];
    } else if (this.currentUser?.role?.name === 'Analista de Performance') {
      this.menu = [perf, ...base, ...extra];
    } else {
      this.menu = [...base, ...extra];
    }
  }

  get isMobile(): boolean {
    return window.innerWidth <= 768;
  }

  ngOnInit() {
    if (this.api.isAuthenticated()) {
      this.api.getCurrentUser().subscribe(u => {
        this.currentUser = u;
        this.buildMenu();
      });
    } else {
      this.buildMenu();
    }
    this.loadClients();
  }

  loadClients() {
    this.api.getClients().subscribe(cs => {
      this.clients = cs;
      this.loadProjects();
    });
  }

  loadProjects() {
    this.api.getProjects().subscribe(ps => {
      this.projectsByClient = {};
      ps.forEach(p => {
        if (!this.projectsByClient[p.client_id]) {
          this.projectsByClient[p.client_id] = [];
        }
        this.projectsByClient[p.client_id].push(p);
      });
    });
  }

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

  onNavigate() {
    if (this.isMobile) {
      this.sidebarOpen = false;
    }
  }

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
