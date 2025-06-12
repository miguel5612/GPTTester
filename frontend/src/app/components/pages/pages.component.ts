import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Page } from '../../models';
import { PageService } from '../../services/page.service';
import { PageFormComponent } from './page-form.component';

@Component({
  selector: 'app-pages',
  standalone: true,
  imports: [CommonModule, FormsModule, PageFormComponent],
  template: `
    <div class="main-panel">
      <h1>Páginas</h1>
      <div class="mb-3 d-flex gap-2">
        <input class="form-control" [(ngModel)]="search" placeholder="Buscar" (ngModelChange)="load()">
        <button class="btn btn-primary" (click)="new()">Nueva</button>
      </div>
      <table class="table table-bordered" *ngIf="filtered.length > 0">
        <thead>
          <tr>
            <th>Nombre</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let p of filtered">
            <td>{{ p.name }}</td>
            <td>
              <button class="btn btn-sm btn-secondary mr-2" (click)="edit(p)">Editar</button>
              <button class="btn btn-sm btn-danger" (click)="remove(p)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="filtered.length === 0">No hay páginas.</div>

      <app-page-form *ngIf="showForm" [page]="editing" (saved)="onSaved()" (cancel)="showForm=false"></app-page-form>
    </div>
  `,
  styles: [`
    .gap-2 { gap: 0.5rem; }
    .mr-2 { margin-right: 0.25rem; }
  `]
})
export class PagesComponent implements OnInit {
  pages: Page[] = [];
  search = '';
  showForm = false;
  editing: Page | null = null;

  constructor(private service: PageService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.service.getPages().subscribe(p => {
      this.pages = p;
      this.filter();
    });
  }

  filter() {
    const term = this.search.toLowerCase();
    this.filtered = this.pages.filter(p => p.name.toLowerCase().includes(term));
  }

  filtered: Page[] = [];

  new() {
    this.editing = null;
    this.showForm = true;
  }

  edit(p: Page) {
    this.editing = p;
    this.showForm = true;
  }

  remove(p: Page) {
    if (confirm('¿Eliminar página?')) {
      this.service.deletePage(p.id).subscribe(() => this.load());
    }
  }

  onSaved() {
    this.showForm = false;
    this.load();
  }
}
