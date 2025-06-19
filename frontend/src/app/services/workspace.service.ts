import { Injectable, EventEmitter } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class WorkspaceService {
  private clientSubject = new BehaviorSubject<number | null>(
    WorkspaceService.loadNumber('clientId')
  );
  currentClient$ = this.clientSubject.asObservable();

  private projectSubject = new BehaviorSubject<number | null>(
    WorkspaceService.loadNumber('projectId')
  );
  currentProject$ = this.projectSubject.asObservable();

  workspaceChanged = new EventEmitter<void>();

  private static loadNumber(key: string): number | null {
    const value = localStorage.getItem(key);
    return value !== null ? Number(value) : null;
  }

  setWorkspace(clientId: number, projectId: number): void {
    localStorage.setItem('clientId', String(clientId));
    localStorage.setItem('projectId', String(projectId));
    this.clientSubject.next(clientId);
    this.projectSubject.next(projectId);
    this.workspaceChanged.emit();
  }

  clearWorkspace(): void {
    localStorage.removeItem('clientId');
    localStorage.removeItem('projectId');
    this.clientSubject.next(null);
    this.projectSubject.next(null);
    this.workspaceChanged.emit();
  }

  hasWorkspace(): boolean {
    return (
      this.clientSubject.value !== null &&
      this.projectSubject.value !== null
    );
  }

  get clientId(): number | null {
    return this.clientSubject.value;
  }

  get projectId(): number | null {
    return this.projectSubject.value;
  }
}
