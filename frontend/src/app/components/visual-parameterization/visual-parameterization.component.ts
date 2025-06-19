import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DragDropModule, CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { PageService } from '../../services/page.service';
import { ElementService } from '../../services/element.service';
import { ActionService } from '../../services/action.service';
import { Page, PageElement, Action } from '../../models';

interface Step {
  id: number;
  type: 'action' | 'if' | 'loop';
  element?: PageElement;
  actionId?: number | null;
  params?: { [key: string]: string };
  condition?: string; // for if
  repeat?: number; // for loop
  steps?: Step[]; // nested steps
  elseSteps?: Step[]; // for if
}

@Component({
  selector: 'app-visual-parameterization',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  template: `
    <div class="container-fluid visual-param">
      <div class="row">
        <div class="col-md-3 sidebar" *ngIf="showColumn('left')">
          <h5>Páginas</h5>
          <ul class="list-group mb-3">
            <li class="list-group-item" *ngFor="let p of pages" (click)="selectPage(p)" [class.active]="selectedPage?.id===p.id">
              {{p.name}}
            </li>
          </ul>
          <h6>Elementos</h6>
          <div cdkDropList id="elements" [cdkDropListData]="elements">
            <div class="element-item" *ngFor="let e of filteredElements" cdkDrag>{{e.name}}</div>
          </div>
        </div>

        <div class="col-md-6 builder" cdkDropList [cdkDropListData]="steps" (cdkDropListDropped)="drop($event)" *ngIf="showColumn('center')">
          <div class="d-flex mb-2">
            <button class="btn btn-sm btn-outline-secondary me-2" (click)="addCondition()">If/Else</button>
            <button class="btn btn-sm btn-outline-secondary" (click)="addLoop()">Loop</button>
          </div>
          <div *ngFor="let s of steps; let i=index" cdkDrag class="step-card">
            <div class="card-body" [ngSwitch]="s.type">
              <div *ngSwitchCase="'action'">
                <div class="d-flex align-items-center mb-2">
                  <span class="handle me-2">☰</span>
                  <strong class="me-2">{{s.element?.name}}</strong>
                  <select class="form-select form-select-sm me-2" [(ngModel)]="s.actionId" (change)="updateParams(s)">
                    <option [ngValue]="null">-- acción --</option>
                    <option *ngFor="let a of actions" [ngValue]="a.id">{{a.name}}</option>
                  </select>
                  <button class="btn btn-sm btn-danger" (click)="removeStep(i)">x</button>
                </div>
                <div *ngIf="s.actionId">
                  <div *ngFor="let key of paramKeys(s)" class="mb-1">
                    <input class="form-control form-control-sm" [(ngModel)]="s.params![key]" [placeholder]="key">
                  </div>
                  <pre class="code-preview">{{previewCode(s)}}</pre>
                </div>
              </div>
              <div *ngSwitchCase="'if'">
                <div class="d-flex align-items-center mb-2">
                  <span class="handle me-2">☰</span>
                  <strong class="me-2">Condición</strong>
                  <button class="btn btn-sm btn-danger" (click)="removeStep(i)">x</button>
                </div>
                <input class="form-control form-control-sm mb-2" [(ngModel)]="s.condition" placeholder="Expresión">
                <div class="ms-3">
                  <small>Then:</small>
                  <div cdkDropList [cdkDropListData]="s.steps" class="nested" (cdkDropListDropped)="dropNested($event, s.steps)">
                    <div *ngFor="let c of s.steps" cdkDrag class="nested-item">
                      {{ displayStep(c) }}
                    </div>
                  </div>
                  <small>Else:</small>
                  <div cdkDropList [cdkDropListData]="s.elseSteps" class="nested" (cdkDropListDropped)="dropNested($event, s.elseSteps)">
                    <div *ngFor="let c of s.elseSteps" cdkDrag class="nested-item">
                      {{ displayStep(c) }}
                    </div>
                  </div>
                </div>
              </div>
              <div *ngSwitchCase="'loop'">
                <div class="d-flex align-items-center mb-2">
                  <span class="handle me-2">☰</span>
                  <strong class="me-2">Loop</strong>
                  <button class="btn btn-sm btn-danger" (click)="removeStep(i)">x</button>
                </div>
                <input type="number" class="form-control form-control-sm mb-2" [(ngModel)]="s.repeat" placeholder="Repeticiones">
                <div cdkDropList [cdkDropListData]="s.steps" class="nested" (cdkDropListDropped)="dropNested($event, s.steps)">
                  <div *ngFor="let c of s.steps" cdkDrag class="nested-item">
                    {{ displayStep(c) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 sidebar" *ngIf="showColumn('right')">
          <h5>Acciones</h5>
          <ul class="list-group">
            <li class="list-group-item" *ngFor="let a of actions">{{a.name}}</li>
          </ul>
          <h6 class="mt-3">Variables globales</h6>
          <textarea class="form-control" rows="4" [(ngModel)]="globalVars"></textarea>
          <div class="mt-2">
            <button class="btn btn-secondary me-2" (click)="togglePreview()">Preview</button>
            <button class="btn btn-primary" (click)="save()">Guardar</button>
          </div>
        </div>
      </div>

      <pre *ngIf="showPreview" class="mt-3 bg-light p-2">{{steps | json}}</pre>
    </div>
  `,
  styles: [`
    .visual-param { padding: 0.5rem; }
    .sidebar { border-right: 1px solid #ccc; max-height: 80vh; overflow:auto; }
    .builder { min-height: 300px; border: 1px dashed #ccc; padding: 0.5rem; }
    .element-item { border:1px solid #ddd; padding:2px 4px; margin-bottom:4px; cursor: move; background:#fff; }
    .step-card { border:1px solid #ddd; padding:0.5rem; margin-bottom:0.5rem; background:#fafafa; }
    .handle { cursor:move; }
    .code-preview { background:#f0f0f0; padding:4px; white-space:pre-wrap; }
    .nested { min-height:40px; border:1px dashed #bbb; padding:2px 4px; margin-bottom:4px; }
    .nested-item { padding:2px 4px; border:1px solid #ddd; margin-bottom:2px; background:#fff; cursor:move; }
    @media (max-width: 768px) {
      .sidebar { display:none; }
      .visual-param.mobile-left .sidebar.left { display:block; width:100%; border-right:none; }
      .visual-param.mobile-center .builder { width:100%; }
      .visual-param.mobile-right .sidebar.right { display:block; width:100%; border-right:none; }
    }
  `]
})
export class VisualParameterizationComponent implements OnInit {
  pages: Page[] = [];
  elements: PageElement[] = [];
  actions: Action[] = [];
  steps: Step[] = [];

  selectedPage: Page | null = null;
  showPreview = false;
  globalVars = '';

  constructor(private pageService: PageService, private elementService: ElementService, private actionService: ActionService) {}

  ngOnInit() {
    this.pageService.getPages().subscribe(p => this.pages = p);
    this.elementService.getElements().subscribe(e => this.elements = e);
    this.actionService.getActions().subscribe(a => this.actions = a);
    this.load();
  }

  showColumn(position: 'left' | 'center' | 'right'): boolean {
    if (window.innerWidth > 768) return true;
    if (position === 'left') return this.viewState === 0;
    if (position === 'center') return this.viewState === 1;
    return this.viewState === 2;
  }

  viewState = 0;

  selectPage(p: Page) { this.selectedPage = p; }

  get filteredElements(): PageElement[] {
    if (!this.selectedPage) return this.elements;
    return this.elements.filter(e => e.page_id === this.selectedPage!.id);
  }

  drop(event: CdkDragDrop<any>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(this.steps, event.previousIndex, event.currentIndex);
    } else {
      const el = event.previousContainer.data[event.previousIndex] as PageElement;
      this.steps.push({ id: Date.now(), type: 'action', element: el, actionId: null, params: {} });
    }
  }

  dropNested(event: CdkDragDrop<any>, list: Step[]) {
    if (event.previousContainer === event.container) {
      moveItemInArray(list, event.previousIndex, event.currentIndex);
    } else {
      const el = event.previousContainer.data[event.previousIndex] as PageElement;
      list.push({ id: Date.now(), type: 'action', element: el, actionId: null, params: {} });
    }
  }

  removeStep(i: number) { this.steps.splice(i, 1); }

  addCondition() {
    this.steps.push({ id: Date.now(), type: 'if', condition: '', steps: [], elseSteps: [] });
  }

  addLoop() {
    this.steps.push({ id: Date.now(), type: 'loop', repeat: 1, steps: [] });
  }

  paramKeys(s: Step): string[] {
    const action = this.actions.find(a => a.id === s.actionId);
    if (!action || !action.argumentos) return [];
    return action.argumentos.split(',').map(a => a.trim()).filter(a => !!a);
  }

  updateParams(s: Step) {
    s.params = {};
    for (const k of this.paramKeys(s)) {
      s.params[k] = '';
    }
  }

  displayStep(s: Step): string {
    if (s.type === 'action') {
      return s.element?.name || '';
    }
    if (s.type === 'if') {
      return 'IF (' + (s.condition || '') + ')';
    }
    return 'LOOP x' + (s.repeat || 1);
  }

  previewCode(s: Step): string {
    const action = this.actions.find(a => a.id === s.actionId);
    if (!action) return '';
    let code = action.codigo;
    for (const k of this.paramKeys(s)) {
      code = code.replace(new RegExp(`\${k}`, 'g'), s.params?.[k] || '');
    }
    return code;
  }

  togglePreview() { this.showPreview = !this.showPreview; }

  validate(): boolean {
    for (const s of this.steps) {
      if (s.type === 'action' && !s.actionId) return false;
      if (s.type === 'if' && !s.condition) return false;
      if (s.type === 'loop' && !s.repeat) return false;
    }
    return true;
  }

  save() {
    if (!this.validate()) { alert('Flujo inválido'); return; }
    localStorage.setItem('visualParamSteps', JSON.stringify(this.steps));
    localStorage.setItem('visualParamGlobals', this.globalVars);
    alert('Guardado en localStorage');
  }

  load() {
    const saved = localStorage.getItem('visualParamSteps');
    if (saved) this.steps = JSON.parse(saved);
    const vars = localStorage.getItem('visualParamGlobals');
    if (vars) this.globalVars = vars;
  }
}
