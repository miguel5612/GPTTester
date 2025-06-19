import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { WorkspaceService } from './services/workspace.service';

export const canActivateWorkspace: CanActivateFn = () => {
  const workspace = inject(WorkspaceService);
  const router = inject(Router);
  return workspace.hasWorkspace()
    ? true
    : router.createUrlTree(['/workspace']);
};
