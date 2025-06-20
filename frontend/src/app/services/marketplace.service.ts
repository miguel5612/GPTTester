import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { MarketplaceComponent, MarketplaceComponentCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class MarketplaceService {
  constructor(private api: ApiService) {}

  getComponents(): Observable<MarketplaceComponent[]> {
    return this.api.getMarketplaceComponents();
  }

  createComponent(c: MarketplaceComponentCreate): Observable<MarketplaceComponent> {
    return this.api.createMarketplaceComponent(c);
  }

  updateComponent(id: number, c: MarketplaceComponentCreate): Observable<MarketplaceComponent> {
    return this.api.updateMarketplaceComponent(id, c);
  }

  deleteComponent(id: number): Observable<any> {
    return this.api.deleteMarketplaceComponent(id);
  }
}
