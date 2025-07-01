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
        path: 'actors',
        loadComponent: () => import('./components/actors/actors.component').then(m => m.ActorsComponent)
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
