import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Role, RoleCreate } from '../models';

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
}
