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

  updateUserRole(id: number, role: UserRoleUpdate): Observable<User> {
    return this.api.updateUserRole(id, role);
  }
}
