import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'workspace',
    loadComponent: () => import('./components/workspace-selector/workspace-selector.component').then(m => m.WorkspaceSelectorComponent)
  },
  {
    path: 'users',
    loadComponent: () => import('./components/users/users.component').then(m => m.UsersComponent),
    canActivate: [() => import('./admin.guard').then(m => m.adminGuard)]
  },
  {
    path: 'register',
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'roles',
    loadComponent: () => import('./components/roles/roles.component').then(m => m.RolesComponent)
  },
  {
    path: 'flow-builder',
    loadComponent: () => import('./components/flow-builder/flow-builder.component').then(m => m.FlowBuilderComponent)
  },
  {
    path: 'test-plans',
    loadComponent: () => import('./components/test-plans/test-plans.component').then(m => m.TestPlansComponent)
  },
  {
    path: 'test-cases',
    loadComponent: () => import('./components/test-cases/test-cases.component').then(m => m.TestCasesComponent)
  },
  {
    path: 'pages',
    loadComponent: () => import('./components/pages/pages.component').then(m => m.PagesComponent)
  },
  {
    path: 'elements',
    loadComponent: () => import('./components/elements/elements.component').then(m => m.ElementsComponent)
  },
  {
    path: 'actions',
    loadComponent: () => import('./components/actions/actions.component').then(m => m.ActionsComponent)
  },
  {
    path: 'agents',
    loadComponent: () => import('./components/agents/agents.component').then(m => m.AgentsComponent)
  },
  {
    path: 'projects',
    loadComponent: () => import('./components/client-admin/client-projects.component').then(m => m.ClientProjectsComponent)
  },
  {
    path: 'service-manager',
    loadComponent: () => import('./components/service-manager/service-manager.component').then(m => m.ServiceManagerComponent)
  },
  {
    path: 'client-admin',
    loadComponent: () => import('./components/client-admin/client-admin.component').then(m => m.ClientAdminComponent)
  },
  {
    path: 'actors',
    loadComponent: () => import('./components/actors/actors.component').then(m => m.ActorsComponent)
  },
  {
    path: 'execution',
    loadComponent: () => import('./components/execution/execution.component').then(m => m.ExecutionComponent)
  },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];
