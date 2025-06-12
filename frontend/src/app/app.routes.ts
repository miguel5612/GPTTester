import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
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
    path: 'actors',
    loadComponent: () => import('./components/actors/actors.component').then(m => m.ActorsComponent)
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
    path: 'execution',
    loadComponent: () => import('./components/execution/execution.component').then(m => m.ExecutionComponent)
  },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];
