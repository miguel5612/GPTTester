import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: '',
    loadComponent: () => import('./components/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    canActivate: [() => import('./auth.guard').then(m => m.authGuard)],
    children: [
      { path: '', redirectTo: 'clients', pathMatch: 'full' },
      {
        path: 'clients',
        loadComponent: () => import('./components/client-admin/client-admin.component').then(m => m.ClientAdminComponent)
      },
      {
        path: 'clients/:clientId/actors',
        loadComponent: () => import('./components/actors/actors.component').then(m => m.ActorsComponent)
      },
      {
        path: 'clients/:clientId/projects',
        loadComponent: () => import('./components/projects/projects.component').then(m => m.ProjectsComponent)
      },
      {
        path: 'projects/:projectId/scenarios',
        loadComponent: () => import('./components/scenarios/scenarios.component').then(m => m.ScenariosComponent)
      },
      {
        path: 'projects/:projectId/scenarios/:scenarioId/tasks',
        loadComponent: () => import('./components/tasks/tasks.component').then(m => m.TasksComponent)
      },
      {
        path: 'projects/:projectId/scenarios/:scenarioId/data',
        loadComponent: () => import('./components/scenario-data/scenario-data.component').then(m => m.ScenarioDataComponent)
      },
      {
        path: 'projects/:projectId/features',
        loadComponent: () => import('./components/features/features.component').then(m => m.FeaturesComponent)
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'users',
        loadComponent: () => import('./components/users/users.component').then(m => m.UsersComponent),
        canActivate: [() => import('./admin.guard').then(m => m.adminGuard)]
      },
      {
        path: 'roles',
        loadComponent: () => import('./components/roles/roles.component').then(m => m.RolesComponent),
        canActivate: [() => import('./admin.guard').then(m => m.adminGuard)]
      },
      {
        path: 'permissions',
        loadComponent: () => import('./components/permissions/permissions.component').then(m => m.PermissionsComponent),
        canActivate: [() => import('./admin.guard').then(m => m.adminGuard)]
      },
      {
        path: 'agents',
        loadComponent: () => import('./components/agents/agents.component').then(m => m.AgentsComponent),
        canActivate: [() => import('./admin.guard').then(m => m.adminGuard)]
      },
      {
        path: 'interactions',
        loadComponent: () => import('./components/interactions/interactions.component').then(m => m.InteractionsComponent)
      },
      {
        path: 'architect/pending',
        loadComponent: () => import('./components/architect/architect-pending.component').then(m => m.ArchitectPendingComponent),
        canActivate: [() => import('./architect.guard').then(m => m.architectGuard)]
      },
      {
        path: 'architect/metrics',
        loadComponent: () => import('./components/architect/architect-metrics.component').then(m => m.ArchitectMetricsComponent),
        canActivate: [() => import('./architect.guard').then(m => m.architectGuard)]
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
