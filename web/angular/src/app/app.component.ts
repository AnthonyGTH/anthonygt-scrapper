import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <mat-toolbar color="primary">
      <span>Price Monitoring System</span>
      <span class="spacer"></span>
      <button mat-icon-button>
        <mat-icon>notifications</mat-icon>
      </button>
    </mat-toolbar>
    
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .spacer {
      flex: 1 1 auto;
    }
    
    main {
      padding: 20px;
    }
  `]
})
export class AppComponent {
  title = 'Price Monitoring System';
}
