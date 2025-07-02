import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Feature } from '../models';

@Injectable({ providedIn: 'root' })
export class FeatureService {
  constructor(private api: ApiService) {}

  getFeatures(): Observable<Feature[]> {
    return this.api.getFeatures();
  }

  createFeature(feature: Feature): Observable<Feature> {
    return this.api.createFeature(feature);
  }
}
