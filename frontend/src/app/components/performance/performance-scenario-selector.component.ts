import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PerformanceService } from '../../services/performance.service';
import { Scenario } from '../../models';

@Component({
  selector: 'app-performance-scenario-selector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="mb-3">
      <label class="form-label">Escenario</label>
      <select class="form-select" [(ngModel)]="selectedId" (change)="onSelect()">
        <option [ngValue]="null">Seleccione...</option>
        <option *ngFor="let s of scenarios" [ngValue]="s.id">{{ s.name }}</option>
      </select>
    </div>
  `
})
export class PerformanceScenarioSelectorComponent implements OnInit {
  scenarios: Scenario[] = [];
  selectedId: number | null = null;
  @Output() selected = new EventEmitter<Scenario | null>();

  constructor(private service: PerformanceService) {}

  ngOnInit() {
    this.service.getScenarios().subscribe(s => (this.scenarios = s));
  }

  onSelect() {
    const sc = this.scenarios.find(s => s.id === this.selectedId) || null;
    this.selected.emit(sc);
  }
}
