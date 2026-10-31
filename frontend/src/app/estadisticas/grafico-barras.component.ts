// Barras horizontales hechas con una tabla HTML: el gráfico ES su propia tabla accesible.
// Se usa para país, subregión, magnitud y profundidad. No necesita ninguna librería.
import { Component, computed, input } from '@angular/core';

// Una barra. Sin color propio, usa el de la serie.
export type FilaBarra = { etiqueta: string; n: number; color?: string };

const COLOR_SERIE = '#176b70';                          // una sola serie, un solo color

@Component({
  selector: 'app-grafico-barras', standalone: true,
  templateUrl: './grafico-barras.component.html', styleUrl: './grafico-barras.component.css'
})
export class GraficoBarrasComponent {
  readonly titulo = input.required<string>();
  readonly filas = input.required<FilaBarra[]>();
  readonly limite = input<number | null>(null);         // cuántas barras se ven; null = todas

  // Si hay más filas que el límite, las que sobran se suman en «Otros»: así el total no cambia.
  readonly visibles = computed<FilaBarra[]>(() => {
    const limite = this.limite();
    const filas = this.filas();
    if (limite === null || filas.length <= limite) return filas;
    const resto = filas.slice(limite);
    return [...filas.slice(0, limite), { etiqueta: `Otros (${resto.length} más)`, n: resto.reduce((suma, f) => suma + f.n, 0) }];
  });
  readonly agrupado = computed(() => this.visibles() !== this.filas());   // visibles() es una lista nueva solo si agrupa
  // La barra más larga marca el 100 %. Todas parten de cero, así que las longitudes se pueden comparar.
  private readonly maximo = computed(() => Math.max(1, ...this.visibles().map(f => f.n)));

  ancho(n: number): number { return n / this.maximo() * 100; }
  color(fila: FilaBarra): string { return fila.color ?? COLOR_SERIE; }
  cifra(n: number): string { return n.toLocaleString('es-ES'); }
}
