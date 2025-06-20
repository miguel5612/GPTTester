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
    path: 'workspace',
    loadComponent: () => import('./components/workspace-selector/workspace-selector.component').then(m => m.WorkspaceSelectorComponent)
  },
  {
    path: '',
    loadComponent: () => import('./components/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    canActivate: [() => import('./workspace.guard').then(m => m.canActivateWorkspace)],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: 'users', loadComponent: () => import('./components/users/users.component').then(m => m.UsersComponent), canActivate: [() => import('./admin.guard').then(m => m.adminGuard)] },
      { path: 'roles', loadComponent: () => import('./components/roles/roles.component').then(m => m.RolesComponent) },
      { path: 'flow-builder', loadComponent: () => import('./components/flow-builder/flow-builder.component').then(m => m.FlowBuilderComponent) },
      { path: 'test-plans', loadComponent: () => import('./components/test-plans/test-plans.component').then(m => m.TestPlansComponent) },
      { path: 'test-cases', loadComponent: () => import('./components/test-cases/test-cases.component').then(m => m.TestCasesComponent) },
      { path: 'scripts', loadComponent: () => import('./components/scripts/scripts.component').then(m => m.ScriptsComponent) },
      { path: 'bdd-builder', loadComponent: () => import('./components/scripts/bdd-script-wizard.component').then(m => m.BddScriptWizardComponent) },
      { path: 'parameterization/:testId', loadComponent: () => import('./components/parameterization/parameterization.component').then(m => m.ParameterizationComponent) },
      { path: 'visual-param', loadComponent: () => import('./components/visual-parameterization/visual-parameterization.component').then(m => m.VisualParameterizationComponent) },
      { path: 'pages', loadComponent: () => import('./components/pages/pages.component').then(m => m.PagesComponent) },
      { path: 'elements', loadComponent: () => import('./components/elements/elements.component').then(m => m.ElementsComponent) },
      { path: 'actions', loadComponent: () => import('./components/actions/actions.component').then(m => m.ActionsComponent) },
      { path: 'agents', loadComponent: () => import('./components/agents/agents.component').then(m => m.AgentsComponent) },
      { path: 'marketplace', loadComponent: () => import('./components/marketplace/marketplace.component').then(m => m.MarketplaceComponent) },
      { path: 'projects', loadComponent: () => import('./components/client-admin/client-projects.component').then(m => m.ClientProjectsComponent) },
      { path: 'service-manager', loadComponent: () => import('./components/service-manager/service-manager.component').then(m => m.ServiceManagerComponent) },
      { path: 'client-admin', loadComponent: () => import('./components/client-admin/client-admin.component').then(m => m.ClientAdminComponent) },
      { path: 'actors', loadComponent: () => import('./components/actors/actors.component').then(m => m.ActorsComponent) },
      { path: 'execution', loadComponent: () => import('./components/execution/execution.component').then(m => m.ExecutionComponent) },
      { path: 'execution-monitor', loadComponent: () => import('./components/execution/execution-monitor-page.component').then(m => m.ExecutionMonitorPageComponent) },
      { path: 'bi', loadComponent: () => import('./components/bi-dashboard/bi-dashboard.component').then(m => m.BiDashboardComponent) }
    ]
  },
  { path: '**', redirectTo: '' }
];
