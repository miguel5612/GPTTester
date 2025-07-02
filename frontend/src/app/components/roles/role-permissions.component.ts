import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Role, PagePermission, PagePermissionCreate, ApiPermission, ApiPermissionCreate } from '../../models';
import { RoleService } from '../../services/role.service';

@Component({
  selector: 'app-role-permissions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal" (click)="close.emit()">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h3>Permisos de {{ role?.name }}</h3>
          <button class="btn-close" (click)="close.emit()">×</button>
        </div>
        <div class="modal-body">
          <h4>Páginas</h4>
          <div *ngFor="let p of pages" class="perm-row">
            <span>{{ p.page }}</span>
            <button class="btn btn-sm btn-danger" (click)="removePage(p)">Quitar</button>
          </div>
          <form class="d-flex mb-3" (ngSubmit)="addPage()">
            <input class="form-control me-2" placeholder="/ruta" [(ngModel)]="newPage.page" name="page" required>
            <button class="btn btn-primary btn-sm" type="submit">Agregar</button>
          </form>
          <h4>APIs</h4>
          <div *ngFor="let a of apis" class="perm-row">
            <span>{{ a.method }} {{ a.route }}</span>
            <button class="btn btn-sm btn-danger" (click)="removeApi(a)">Quitar</button>
          </div>
          <form class="d-flex mb-3" (ngSubmit)="addApi()">
            <input class="form-control me-2" placeholder="/api/ruta" [(ngModel)]="newApi.route" name="route" required>
            <select class="form-select me-2" [(ngModel)]="newApi.method" name="method" required>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
            <button class="btn btn-primary btn-sm" type="submit">Agregar</button>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" (click)="close.emit()">Cerrar</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal-content {
      background: white;
      border-radius: 10px;
      width: 90%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      border-bottom: 1px solid #eee;
    }
    .modal-body {
      padding: 20px;
    }
    .perm-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 0;
    }
    .modal-footer {
      display: flex;
      justify-content: flex-end;
      padding: 20px;
      border-top: 1px solid #eee;
    }
    .btn-close {
      background: none;
      border: none;
      font-size: 1.2rem;
      cursor: pointer;
    }
  `]
})
export class RolePermissionsComponent implements OnChanges {
  @Input() role!: Role;
  @Output() close = new EventEmitter<void>();

  pages: PagePermission[] = [];
  apis: ApiPermission[] = [];

  newPage: PagePermissionCreate = { page: '' };
  newApi: ApiPermissionCreate = { route: '', method: 'GET' };

  constructor(private service: RoleService) {}

  ngOnChanges() {
    if (this.role) {
      this.load();
    }
  }

  load() {
    this.service.getPagePermissions(this.role.id).subscribe(p => this.pages = p);
    this.service.getApiPermissions(this.role.id).subscribe(a => this.apis = a);
  }

  addPage() {
    if (!this.newPage.page) return;
    this.service.addPagePermission(this.role.id, this.newPage).subscribe(p => {
      this.pages.push(p);
      this.newPage = { page: '' };
    });
  }

  removePage(p: PagePermission) {
    if (!confirm('¿Quitar permiso?')) return;
    this.service.deletePagePermission(this.role.id, p.page).subscribe(() => {
      this.pages = this.pages.filter(x => x.id !== p.id);
    });
  }

  addApi() {
    if (!this.newApi.route || !this.newApi.method) return;
    this.service.addApiPermission(this.role.id, this.newApi).subscribe(a => {
      this.apis.push(a);
      this.newApi = { route: '', method: 'GET' };
    });
  }

  removeApi(a: ApiPermission) {
    if (!confirm('¿Quitar permiso?')) return;
    this.service.deleteApiPermission(this.role.id, a.id).subscribe(() => {
      this.apis = this.apis.filter(x => x.id !== a.id);
    });
  }
}
