import { Component, Input, HostBinding } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-responsive-grid',
  standalone: true,
  imports: [CommonModule],
  template: `<div class="grid"><ng-content></ng-content></div>`,
  styles: [`
    :host { display:block; container-type:inline-size; }
    .grid { display:grid; gap:var(--gap,1rem); grid-template-columns:repeat(var(--cols-mobile,1),1fr); }
    @container (min-width:600px) { .grid { grid-template-columns:repeat(var(--cols-tablet,2),1fr); } }
    @container (min-width:900px) { .grid { grid-template-columns:repeat(var(--cols-desktop,4),1fr); } }
  `]
})
export class ResponsiveGridComponent {
  @Input() mobileCols = 1;
  @Input() tabletCols = 2;
  @Input() desktopCols = 4;
  @Input() gap = '1rem';

  @HostBinding('style.--cols-mobile') get colsMobile() { return this.mobileCols; }
  @HostBinding('style.--cols-tablet') get colsTablet() { return this.tabletCols; }
  @HostBinding('style.--cols-desktop') get colsDesktop() { return this.desktopCols; }
  @HostBinding('style.--gap') get hostGap() { return this.gap; }
}
