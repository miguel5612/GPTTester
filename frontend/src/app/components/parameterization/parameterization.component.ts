import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DragDropModule, CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { PageService } from '../../services/page.service';
import { ElementService } from '../../services/element.service';
import { ActionService } from '../../services/action.service';
import { TestCaseService } from '../../services/test-case.service';
import { Page, PageElement, Action } from '../../models';
import { firstValueFrom } from 'rxjs';

interface Step {
  id?: number;
  element: PageElement;
  actionId: number | null;
  params: string;
}

@Component({
  selector: 'app-parameterization',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  template: `
    <div class="param-container">
      <div class="row mb-3">
        <div class="col">
          <h4>Páginas disponibles</h4>
          <ul class="list-group small">
            <li class="list-group-item" *ngFor="let p of pages" (click)="selectPage(p)" [class.active]="selectedPage?.id===p.id">
              {{p.name}}
            </li>
          </ul>
        </div>
        <div class="col">
          <h4>Elementos</h4>
          <div cdkDropList id="elementsList" [cdkDropListData]="elements">
            <div class="border p-1 mb-1" *ngFor="let el of filteredElements" cdkDrag>{{el.name}}</div>
          </div>
        </div>
        <div class="col">
          <h4>Acciones</h4>
          <div cdkDropList [cdkDropListData]="steps" class="builder" (cdkDropListDropped)="drop($event)">
            <div class="border p-1 mb-1 d-flex align-items-center" *ngFor="let s of steps; let i=index" cdkDrag>
              <span class="handle me-1">☰</span>
              <span class="me-1">{{s.element.name}}</span>
              <select class="form-select form-select-sm me-1" [(ngModel)]="s.actionId">
                <option [ngValue]="null">--acción--</option>
                <option *ngFor="let a of actions" [ngValue]="a.id">{{a.name}}</option>
              </select>
              <input class="form-control form-control-sm me-1" [(ngModel)]="s.params" placeholder="Params JSON">
              <button class="btn btn-sm btn-danger" (click)="removeStep(i)">x</button>
            </div>
          </div>
        </div>
      </div>
      <div class="mt-2">
        <button class="btn btn-secondary me-2" (click)="togglePreview()">Vista previa</button>
        <button class="btn btn-primary" (click)="save()">Guardar</button>
      </div>
      <pre *ngIf="showPreview" class="mt-3 bg-light p-2">{{steps}}</pre>
    </div>
  `,
  styles: [`
    .builder { min-height: 200px; border: 1px dashed #ccc; padding: 0.5rem; }
    .handle { cursor: move; }
    li.active { background:#eef; cursor:pointer; }
    li { cursor:pointer; }
  `]
})
export class ParameterizationComponent implements OnInit {
  @Input() testId!: number;

  pages: Page[] = [];
  elements: PageElement[] = [];
  actions: Action[] = [];
  steps: Step[] = [];

  selectedPage: Page | null = null;
  showPreview = false;
  private originalIds: number[] = [];

  constructor(
    private pageService: PageService,
    private elementService: ElementService,
    private actionService: ActionService,
    private testService: TestCaseService
  ) {}

  ngOnInit() {
    this.pageService.getPages().subscribe(p => this.pages = p);
    this.elementService.getElements().subscribe(e => this.elements = e);
    this.actionService.getActions().subscribe(a => this.actions = a);
    this.loadAssignments();
  }

  get filteredElements(): PageElement[] {
    if (!this.selectedPage) return this.elements;
    return this.elements.filter(e => e.page_id === this.selectedPage!.id);
  }

  selectPage(p: Page) { this.selectedPage = p; }

  drop(event: CdkDragDrop<any>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(this.steps, event.previousIndex, event.currentIndex);
    } else {
      const el = event.previousContainer.data[event.previousIndex] as PageElement;
      this.steps.push({ element: el, actionId: null, params: '' });
    }
  }

  removeStep(i: number) { this.steps.splice(i, 1); }

  togglePreview() { this.showPreview = !this.showPreview; }

  async loadAssignments() {
    this.elementService.getAssignments().subscribe(asg => {
      const assigned = asg.filter(a => a.test_id === this.testId);
      this.originalIds = assigned.map(a => a.id);
      this.steps = assigned.map(a => {
        const el = this.elements.find(e => e.id === a.element_id)!;
        return { id: a.id, element: el, actionId: a.action_id, params: JSON.stringify(a.parametros || {}) };
      });
    });
  }

  async save() {
    for (const s of this.steps) {
      if (!s.actionId) { alert('Seleccione acción para todos los pasos'); return; }
      let parametros: any = undefined;
      if (s.params) {
        try { parametros = JSON.parse(s.params); } catch { alert('Parámetros inválidos'); return; }
      }
      await firstValueFrom(this.elementService.addToTest(s.element.id, this.testId));
      if (s.id) {
        await firstValueFrom(this.actionService.updateAssignment(s.id, {
          action_id: s.actionId,
          element_id: s.element.id,
          test_id: this.testId,
          parametros
        }));
      } else {
        const newAsg = await firstValueFrom(this.actionService.createAssignment({
          action_id: s.actionId,
          element_id: s.element.id,
          test_id: this.testId,
          parametros
        }));
        s.id = newAsg.id;
      }
    }
    // Delete removed assignments
    const toDelete = this.originalIds.filter(id => !this.steps.some(s => s.id === id));
    for (const id of toDelete) {
      await firstValueFrom(this.actionService.deleteAssignment(id));
    }
    await firstValueFrom(this.testService.updateTestCase(this.testId, { status: 'parametrizado' } as any));
    alert('Guardado');
  }
}
