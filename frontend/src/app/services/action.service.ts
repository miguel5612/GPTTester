import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Action, ActionCreate, ActionAssignment, ActionAssignmentCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ActionService {
  constructor(private api: ApiService) {}

  getActions(search?: string, tipo?: string): Observable<Action[]> {
    return this.api.getActions(search, tipo);
  }

  getAction(id: number): Observable<Action> {
    return this.api.getAction(id);
  }

  createAction(action: ActionCreate): Observable<Action> {
    return this.api.createAction(action);
  }

  updateAction(id: number, action: ActionCreate): Observable<Action> {
    return this.api.updateAction(id, action);
  }

  deleteAction(id: number): Observable<any> {
    return this.api.deleteAction(id);
  }

  getAssignments(): Observable<ActionAssignment[]> {
    return this.api.getAssignments();
  }

  createAssignment(a: ActionAssignmentCreate): Observable<ActionAssignment> {
    return this.api.createAssignment(a);
  }

  updateAssignment(id: number, a: ActionAssignmentCreate): Observable<ActionAssignment> {
    return this.api.updateAssignment(id, a);
  }

  deleteAssignment(id: number): Observable<any> {
    return this.api.deleteAssignment(id);
  }
}
