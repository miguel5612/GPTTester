import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { DigitalAsset, DigitalAssetCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class DigitalAssetService {
  constructor(private api: ApiService) {}

  getAssets(clientId?: number): Observable<DigitalAsset[]> {
    return this.api.getDigitalAssets(clientId);
  }

  createAsset(asset: DigitalAssetCreate): Observable<DigitalAsset> {
    return this.api.createDigitalAsset(asset);
  }

  updateAsset(id: number, asset: DigitalAssetCreate): Observable<DigitalAsset> {
    return this.api.updateDigitalAsset(id, asset);
  }

  deleteAsset(id: number): Observable<any> {
    return this.api.deleteDigitalAsset(id);
  }
}
