import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Role, RoleCreate, PagePermission, PagePermissionCreate, ApiPermission, ApiPermissionCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class RoleService {
  constructor(private api: ApiService) {}

  getRoles(): Observable<Role[]> {
    return this.api.getRoles();
  }

  createRole(role: RoleCreate): Observable<Role> {
    return this.api.createRole(role);
  }

  updateRole(id: number, role: RoleCreate): Observable<Role> {
    return this.api.updateRole(id, role);
  }

  deleteRole(id: number): Observable<any> {
    return this.api.deleteRole(id);
  }

  getPagePermissions(roleId: number): Observable<PagePermission[]> {
    return this.api.getPagePermissions(roleId);
  }

  addPagePermission(roleId: number, perm: PagePermissionCreate): Observable<PagePermission> {
    return this.api.addPagePermission(roleId, perm);
  }

  deletePagePermission(roleId: number, page: string): Observable<any> {
    return this.api.deletePagePermission(roleId, page);
  }

  getApiPermissions(roleId: number): Observable<ApiPermission[]> {
    return this.api.getApiPermissions(roleId);
  }

  addApiPermission(roleId: number, perm: ApiPermissionCreate): Observable<ApiPermission> {
    return this.api.addApiPermission(roleId, perm);
  }

  deleteApiPermission(roleId: number, permId: number): Observable<any> {
    return this.api.deleteApiPermission(roleId, permId);
  }
}
