import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { ApiService } from './services/api.service';
import { of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

export const managerGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const router = inject(Router);

  if (!api.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  return api.getCurrentUser().pipe(
    map(user =>
      user.role?.name === 'Gerente de servicios'
        ? true
        : router.createUrlTree(['/dashboard'])
    ),
    catchError(() => of(router.createUrlTree(['/dashboard'])))
  );
};
