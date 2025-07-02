import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { ApiService } from './services/api.service';
import { of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

export const performanceGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const router = inject(Router);

  if (!api.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  return api.getCurrentUser().pipe(
    map(user =>
      user.role?.name === 'Analista de Performance'
        ? true
        : router.createUrlTree(['/'])
    ),
    catchError(() => of(router.createUrlTree(['/'])))
  );
};
