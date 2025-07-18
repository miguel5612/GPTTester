import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { User, UserCreate, UserRoleUpdate } from '../models';

@Injectable({ providedIn: 'root' })
export class UserService {
  constructor(private api: ApiService) {}

  getUsers(): Observable<User[]> {
    return this.api.getUsers();
  }

  getUser(id: number): Observable<User> {
    return this.api.getUser(id);
  }

  createUser(user: UserCreate): Observable<User> {
    return this.api.createUser(user);
  }

  updateUser(id: number, data: any): Observable<User> {
    return this.api.updateUser(id, data);
  }

  deleteUser(id: number): Observable<any> {
    return this.api.deleteUser(id);
  }

  updateUserRole(id: number, role: UserRoleUpdate): Observable<User> {
    return this.api.updateUserRole(id, role);
  }

  updateUserActive(id: number, isActive: boolean): Observable<User> {
    return this.api.updateUserActive(id, isActive);
  }
}
