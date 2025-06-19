import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-swipeable-cards',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container" (pointerdown)="start($event)" (pointerup)="end($event)">
      <div class="cards" [style.transform]="'translateX(' + (-current * 100) + '%)'">
        <ng-content></ng-content>
      </div>
    </div>
    <div class="controls" *ngIf="isDesktop">
      <button (click)="prev()" [disabled]="current===0">Prev</button>
      <button (click)="next()" [disabled]="current===count-1">Next</button>
    </div>
  `,
  styles: [`
    :host { display:block; container-type:inline-size; }
    .container { overflow:hidden; touch-action:pan-y; }
    .cards { display:flex; transition:transform 0.3s ease; }
    ::ng-deep > * { flex:0 0 100%; }
    .controls { margin-top:0.5rem; display:flex; gap:0.5rem; justify-content:center; }
    button { padding:0.5rem 1rem; border:none; border-radius:4px; background:var(--btn-primary); color:var(--btn-primary-text); }
    @container (min-width:768px) { .container { touch-action:auto; } }
  `]
})
export class SwipeableCardsComponent {
  @Input() count = 0;
  current = 0;
  private startX = 0;
  isDesktop = false;

  ngOnInit() { this.isDesktop = window.innerWidth >= 768; }

  start(event: PointerEvent) { this.startX = event.clientX; }
  end(event: PointerEvent) {
    const diff = event.clientX - this.startX;
    if (Math.abs(diff) > 50) {
      if (diff < 0) this.next(); else this.prev();
    }
  }
  next() { if (this.current < this.count - 1) this.current++; }
  prev() { if (this.current > 0) this.current--; }
}
