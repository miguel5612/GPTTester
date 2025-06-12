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
    path: 'execution',
    loadComponent: () => import('./components/execution/execution.component').then(m => m.ExecutionComponent)
  },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];
