import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DigitalAsset, Client, DigitalAssetCreate } from '../../models';
import { DigitalAssetService } from '../../services/digital-asset.service';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-digital-assets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="main-panel">
      <h1>Activos Digitales</h1>
      <div class="d-flex gap-2 mb-3">
        <select class="form-control" [(ngModel)]="clientId" (change)="load()">
          <option [ngValue]="null">Cliente</option>
          <option *ngFor="let c of clients" [ngValue]="c.id">{{ c.name }}</option>
        </select>
        <input class="form-control" [(ngModel)]="form.description" placeholder="Descripción">
        <button class="btn btn-primary" (click)="save()">Agregar</button>
      </div>
      <table class="table table-bordered" *ngIf="assets.length > 0">
        <thead>
          <tr><th>Descripción</th><th>Cliente</th><th></th></tr>
        </thead>
        <tbody>
          <tr *ngFor="let a of assets">
            <td>{{ a.description }}</td>
            <td>{{ clientName(a.clientId) }}</td>
            <td><button class="btn btn-sm btn-danger" (click)="remove(a)">Eliminar</button></td>
          </tr>
        </tbody>
      </table>
      <div *ngIf="assets.length === 0">No hay activos.</div>
    </div>
  `,
  styles: [`
    .gap-2 { gap: .5rem; }
  `]
})
export class DigitalAssetsComponent implements OnInit {
  clients: Client[] = [];
  assets: DigitalAsset[] = [];
  clientId: number | null = null;
  form: DigitalAssetCreate = { clientId: 0, description: '' };

  constructor(private assetService: DigitalAssetService, private clientService: ClientService) {}

  ngOnInit() {
    this.clientService.getClients().subscribe(c => this.clients = c);
    this.load();
  }

  load() {
    this.assetService.getAssets(this.clientId || undefined).subscribe(a => this.assets = a);
    if (this.clientId !== null) {
      this.form.clientId = this.clientId;
    }
  }

  clientName(id: number) {
    return this.clients.find(c => c.id === id)?.name || '-';
  }

  save() {
    if (!this.form.clientId || !this.form.description) return;
    this.assetService.createAsset(this.form).subscribe(() => {
      this.form.description = '';
      this.load();
    });
  }

  remove(a: DigitalAsset) {
    if (confirm('¿Eliminar activo digital?')) {
      this.assetService.deleteAsset(a.id).subscribe(() => this.load());
    }
  }
}
