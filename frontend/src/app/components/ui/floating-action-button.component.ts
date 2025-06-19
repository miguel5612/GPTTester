import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface FabAction {
  label: string;
  action: () => void;
}

@Component({
  selector: 'app-floating-action-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="menu" *ngIf="expanded">
      <button *ngFor="let a of actions" (click)="a.action()">{{ a.label }}</button>
    </div>
    <button class="fab" (click)="toggle()">+</button>
  `,
  styles: [`
    :host { position:fixed; bottom:1rem; right:1rem; z-index:1000; container-type:inline-size; }
    .fab { width:56px; height:56px; border-radius:50%; border:none; background:var(--btn-primary); color:var(--btn-primary-text); display:flex; align-items:center; justify-content:center; font-size:2rem; box-shadow:0 2px 8px rgba(0,0,0,0.3); }
    .menu { position:absolute; bottom:70px; right:0; display:flex; flex-direction:column; gap:0.5rem; }
    .menu button { border:none; padding:0.5rem 1rem; border-radius:4px; background:var(--panel-bg); color:var(--title-color); box-shadow:0 2px 4px rgba(0,0,0,0.2); }
    @container (min-width:768px) { :host { position:static; } }
  `]
})
export class FloatingActionButtonComponent {
  @Input() actions: FabAction[] = [];
  expanded = false;

  toggle() { this.expanded = !this.expanded; }
}
