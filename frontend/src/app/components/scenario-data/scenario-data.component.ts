import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-scenario-data',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="main-panel">
      <h1>Datos de Escenario</h1>
      <p>Escenario ID: {{ scenarioId }}</p>
    </div>
  `
})
export class ScenarioDataComponent implements OnInit {
  scenarioId!: number;

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    this.scenarioId = Number(this.route.snapshot.paramMap.get('scenarioId'));
  }
}
