import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Feature } from '../../models';
import { FeatureService } from '../../services/feature.service';

@Component({
  selector: 'app-features',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Features</h1>
      <p>Proyecto ID: {{ projectId }}</p>

      <form (ngSubmit)="create()" class="mb-3">
        <div class="row g-2">
          <div class="col">
            <input class="form-control" [(ngModel)]="newFeature.name" name="name" placeholder="Nombre" required>
          </div>
          <div class="col">
            <input class="form-control" [(ngModel)]="newFeature.description" name="desc" placeholder="Descripción">
          </div>
          <div class="col-auto">
            <button class="btn btn-primary" type="submit">Crear</button>
          </div>
        </div>
      </form>

      <table class="table table-sm" *ngIf="features.length">
        <thead><tr><th>ID</th><th>Nombre</th><th>Descripción</th></tr></thead>
        <tbody>
          <tr *ngFor="let f of features">
            <td>{{f.id}}</td>
            <td>{{f.name}}</td>
            <td>{{f.description}}</td>
          </tr>
        </tbody>
      </table>
      <p *ngIf="!features.length">No hay CP registrados.</p>
    </div>
  `
})
export class FeaturesComponent implements OnInit {
  projectId!: number;
  features: Feature[] = [];
  newFeature: Partial<Feature> = { name: '', description: '' };

  constructor(private route: ActivatedRoute, private service: FeatureService) {}

  ngOnInit() {
    this.projectId = Number(this.route.snapshot.paramMap.get('projectId'));
    this.load();
  }

  load() {
    this.service.getFeatures().subscribe(fs => this.features = fs);
  }

  create() {
    if (!this.newFeature.name) return;
    this.service.createFeature({
      id: 0,
      name: this.newFeature.name!,
      description: this.newFeature.description || '',
      status: true
    }).subscribe(f => {
      this.features.push(f);
      this.newFeature = { name: '', description: '' };
    });
  }
}
