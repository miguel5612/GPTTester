import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { PageElement, PageElementCreate, ActionAssignment, ActionAssignmentCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class ElementService {
  constructor(private api: ApiService) {}

  getElements(): Observable<PageElement[]> {
    return this.api.getElements();
  }

  getElement(id: number): Observable<PageElement> {
    return this.api.getElement(id);
  }

  createElement(el: PageElementCreate): Observable<PageElement> {
    return this.api.createElement(el);
  }

  updateElement(id: number, el: PageElementCreate): Observable<PageElement> {
    return this.api.updateElement(id, el);
  }

  deleteElement(id: number): Observable<any> {
    return this.api.deleteElement(id);
  }

  addToTest(elementId: number, testId: number): Observable<PageElement> {
    return this.api.addElementToTest(elementId, testId);
  }

  removeFromTest(elementId: number, testId: number): Observable<PageElement> {
    return this.api.removeElementFromTest(elementId, testId);
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
