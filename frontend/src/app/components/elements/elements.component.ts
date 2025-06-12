import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ElementService } from '../../services/element.service';
import { PageService } from '../../services/page.service';
import { PageElement, Page } from '../../models';
import { ElementFormComponent } from './element-form.component';

@Component({
  selector: 'app-elements',
  standalone: true,
  imports: [CommonModule, FormsModule, ElementFormComponent],
  template: `
    <div class="main-panel">
      <h1>Localizadores</h1>
      <div class="d-flex flex-wrap gap-2 mb-3">
        <select class="form-control" [(ngModel)]="pageId" (change)="load()">
          <option [ngValue]="null">Página</option>
          <option *ngFor="let p of pages" [ngValue]="p.id">{{ p.name }}</option>
        </select>
        <input class="form-control" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="filter()">
        <button class="btn btn-primary" (click)="new()">Nuevo</button>
      </div>
      <table class="table table-bordered" *ngIf="filtered.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Página</th>
            <th>Tipo</th>
            <th>Estrategia</th>
            <th>Valor</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let e of filtered">
            <td>{{ e.name }}</td>
            <td>{{ pageName(e.page_id) }}</td>
            <td>{{ e.tipo }}</td>
            <td>{{ e.estrategia }}</td>
            <td>{{ e.valor }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(e)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(e)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="filtered.length === 0">No hay elementos.</div>

      <app-element-form *ngIf="showForm" [element]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-element-form>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class ElementsComponent implements OnInit {
  elements: PageElement[] = [];
  pages: Page[] = [];
  filtered: PageElement[] = [];
  pageId: number | null = null;
  search = '';
  showForm = false;
  editing: PageElement | null = null;

  constructor(private service: ElementService, private pageService: PageService) {}

  ngOnInit() {
    this.pageService.getPages().subscribe(p => this.pages = p);
    this.load();
  }

  load() {
    this.service.getElements().subscribe(e => {
      this.elements = e;
      this.filter();
    });
  }

  pageName(id: number) {
    return this.pages.find(p => p.id === id)?.name || '-';
  }

  filter() {
    const term = this.search.toLowerCase();
    this.filtered = this.elements.filter(e => {
      const matchesPage = this.pageId ? e.page_id === this.pageId : true;
      const matchesText = e.name.toLowerCase().includes(term);
      return matchesPage && matchesText;
    });
  }

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(e: PageElement) {
    this.editing = e;
    this.showForm = true;
  }

  remove(e: PageElement) {
    if (confirm('¿Eliminar elemento?')) {
      this.service.deleteElement(e.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
