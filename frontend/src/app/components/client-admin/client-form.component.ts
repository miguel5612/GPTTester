import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Client, ClientCreate } from '../../models';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-client-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-body">
        <h3 class="card-title">{{ client ? 'Editar Cliente' : 'Nuevo Cliente' }}</h3>
        <form (ngSubmit)="save()">
          <div class="mb-3">
            <label class="form-label">Nombre</label>
            <input class="form-control" [(ngModel)]="form.name" name="name" required>
          </div>
          <button class="btn btn-primary" type="submit">Guardar</button>
          <button type="button" class="btn btn-secondary ms-2" (click)="cancel.emit()">Cancelar</button>
        </form>
      </div>
    </div>
  `
})
export class ClientFormComponent implements OnInit {
  @Input() client: Client | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  form: ClientCreate = { name: '' };

  constructor(private service: ClientService) {}

  ngOnInit() {
    if (this.client) {
      this.form = { name: this.client.name };
    }
  }

  save() {
    const obs = this.client
      ? this.service.updateClient(this.client.id, this.form)
      : this.service.createClient(this.form);
    obs.subscribe(() => this.saved.emit());
  }
}
