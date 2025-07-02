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
        path: 'interactions',
        loadComponent: () => import('./components/interactions/interactions.component').then(m => m.InteractionsComponent)
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
