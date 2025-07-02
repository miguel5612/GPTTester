import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Interaction } from '../../models';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-interactions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Interacciones</h1>
      <form class="mb-3" (ngSubmit)="save()">
        <div class="row g-2">
          <div class="col">
            <input class="form-control" placeholder="Código" [(ngModel)]="form.code" name="code" required>
          </div>
          <div class="col">
            <input class="form-control" placeholder="Nombre" [(ngModel)]="form.name" name="name" required>
          </div>
          <div class="col-4">
            <input class="form-control" placeholder="Descripción" [(ngModel)]="form.description" name="description">
          </div>
          <div class="col-auto d-flex align-items-center">
            <label class="form-check-label me-2">
              <input type="checkbox" class="form-check-input" [(ngModel)]="form.requireReview" name="requireReview">
              Requiere revisión
            </label>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary" type="submit">Agregar</button>
          </div>
        </div>
      </form>
      <ul class="list-group">
        <li class="list-group-item" *ngFor="let i of interactions">{{ i.code }} - {{ i.name }}</li>
      </ul>
    </div>
  `
})
export class InteractionsComponent implements OnInit {
  interactions: Interaction[] = [];
  form: Partial<Interaction> = { code: '', name: '', description: '', requireReview: false };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.getInteractions().subscribe(list => this.interactions = list);
  }

  save(): void {
    if (!this.form.code || !this.form.name) return;
    const data: Interaction = {
      id: 0,
      userId: 1,
      code: this.form.code!,
      name: this.form.name!,
      description: this.form.description || '',
      requireReview: !!this.form.requireReview
    };
    this.api.createInteraction(data).subscribe(() => {
      this.form = { code: '', name: '', description: '', requireReview: false };
      this.load();
    });
  }
}
