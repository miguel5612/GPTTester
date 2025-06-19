import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User, Client } from '../../models';
import { ClientService } from '../../services/client.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-client-analysts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card" *ngIf="client">
      <div class="card-body">
        <h3 class="card-title">Analistas de {{ client.name }}</h3>
        <input class="form-control mb-2" placeholder="Buscar..." [(ngModel)]="search" (ngModelChange)="onSearch()" />
        <div *ngFor="let u of analysts" class="form-check d-flex align-items-center mb-1">
          <input class="form-check-input me-2" type="checkbox" [id]="'ca-'+u.id"
            [checked]="isAssigned(u)"
            (change)="toggle(u, $any($event.target).checked)">
          <label class="form-check-label me-2" [for]="'ca-'+u.id">
            {{ u.username }} ({{ u.role.name }})
          </label>
          <input type="number" class="form-control form-control-sm" style="width:80px" [(ngModel)]="dedication[u.id]" placeholder="% dedicación">
        </div>
        <nav class="mt-2">
          <ul class="pagination mb-0">
            <li class="page-item" [class.disabled]="page === 1">
              <button class="page-link" (click)="prev()">Anterior</button>
            </li>
            <li class="page-item"><span class="page-link">{{ page }}</span></li>
            <li class="page-item" [class.disabled]="analysts.length < 10">
              <button class="page-link" (click)="next()" [disabled]="analysts.length < 10">Siguiente</button>
            </li>
          </ul>
        </nav>
        <button class="btn btn-secondary mt-3" (click)="close.emit()">Cerrar</button>
      </div>
    </div>
  `,
  styles: [`
    .form-check { margin-bottom: 0.5rem; }
  `]
})
export class ClientAnalystsComponent implements OnChanges {
  @Input() clientId!: number;
  @Output() updated = new EventEmitter<{ action: string; user: User }>();
  @Output() close = new EventEmitter<void>();

  client: Client | null = null;
  analysts: User[] = [];
  dedication: { [id: number]: number } = {};
  page = 1;
  search = '';

  constructor(private clientService: ClientService, private api: ApiService) {}

  ngOnChanges() {
    if (this.clientId) {
      this.load();
    }
  }

  load() {
    this.clientService.getClients().subscribe(cs => {
      this.client = cs.find(c => c.id === this.clientId) || null;
    });
    this.api.getAnalysts(this.search, this.page).subscribe(users => {

      this.analysts = users;
    });
  }

  onSearch() {
    this.page = 1;
    this.load();
  }

  prev() {
    if (this.page > 1) {
      this.page--;
      this.load();
    }
  }

  next() {
    if (this.analysts.length === 10) {
      this.page++;
      this.load();
    }
  }

  isAssigned(u: User): boolean {
    return this.client?.analysts.some(a => a.id === u.id) ?? false;
  }

  toggle(user: User, checked: boolean) {
    if (!this.client) return;
    const obs = checked
      ? this.clientService.assignAnalyst(this.client.id, user.id, this.dedication[user.id] || 100)
      : this.clientService.unassignAnalyst(this.client.id, user.id);
    obs.subscribe(c => {
      this.client = c;
      const action = checked ? 'added analyst' : 'removed analyst';
      this.updated.emit({ action, user });
    });
  }
}
