// Columnas por ventana fija de 1 hora UTC (hora en que OCURRIÓ el terremoto).
// Todo se dibuja en un solo trazado SVG: un año son unas 8.760 ventanas y un elemento por barra pesaría demasiado.
import { Component, computed, input, signal } from '@angular/core';
import type { Periodo, VentanaHora } from '../api.service';

type Ventana = { inicio: number; n: number; parcial: boolean };

const HORA_MS = 3_600_000;
const MAX_FILAS_TABLA = 168;                            // una semana de horas: más sería una tabla inmanejable
const FILAS_PICO = 24;                                  // con periodos largos, la tabla muestra solo las horas con más eventos
const HUECO = 0.08;                                     // separación entre columnas, en fracción de una ventana

// Redondea hacia arriba a 1, 2 o 5 por una potencia de 10, para que el eje tenga cifras limpias.
function techoLimpio(maximo: number): number {
  if (maximo <= 1) return 1;
  const potencia = 10 ** Math.floor(Math.log10(maximo));
  const escalon = [1, 2, 5, 10].find(e => e * potencia >= maximo) ?? 10;
  return escalon * potencia;
}

@Component({
  selector: 'app-grafico-horas', standalone: true,
  templateUrl: './grafico-horas.component.html', styleUrl: './grafico-horas.component.css'
})
export class GraficoHorasComponent {
  readonly horas = input.required<VentanaHora[]>();
  readonly periodo = input.required<Periodo>();
  readonly seleccion = signal<number | null>(null);     // ventana bajo el ratón

  // Una ventana es parcial si el periodo consultado no la cubre entera (normalmente, la primera y la última).
  readonly ventanas = computed<Ventana[]>(() => {
    const desde = new Date(this.periodo().start).getTime();
    const hasta = new Date(this.periodo().end).getTime();
    return this.horas().map(h => {
      const inicio = new Date(h.hora).getTime();
      return { inicio, n: h.n, parcial: inicio < desde || inicio + HORA_MS > hasta };
    });
  });
  readonly hayParciales = computed(() => this.ventanas().some(v => v.parcial));
  readonly techo = computed(() => techoLimpio(Math.max(0, ...this.ventanas().map(v => v.n))));
  // viewBox: una unidad de ancho = una ventana; una unidad de alto = un terremoto.
  readonly vista = computed(() => `0 0 ${Math.max(1, this.ventanas().length)} ${this.techo()}`);
  readonly trazoCompletas = computed(() => this.trazo(v => !v.parcial));
  readonly trazoParciales = computed(() => this.trazo(v => v.parcial));

  // La ventana con más terremotos: se nombra siempre en texto.
  private readonly pico = computed(() => this.ventanas().reduce<Ventana | null>((a, v) => a === null || v.n > a.n ? v : a, null));

  // Línea de lectura: la ventana señalada o, si no hay ninguna, el resumen.
  readonly lectura = computed(() => {
    const ventanas = this.ventanas();
    const i = this.seleccion();
    if (i !== null && ventanas[i]) return this.describir(ventanas[i]);
    const pico = this.pico();
    if (!pico || pico.n === 0) return 'Ninguna ventana tiene terremotos.';
    const vacias = ventanas.filter(v => v.n === 0).length;
    return `Máximo: ${this.describir(pico)}. Ventanas: ${ventanas.length}, de ellas ${vacias} sin terremotos.`;
  });

  readonly tablaResumida = computed(() => this.ventanas().length > MAX_FILAS_TABLA);
  // Tabla equivalente: todas las ventanas o, en periodos largos, las de más eventos en orden de fecha.
  readonly filasTabla = computed(() => {
    if (!this.tablaResumida()) return this.ventanas();
    return [...this.ventanas()].sort((a, b) => b.n - a.n).slice(0, FILAS_PICO).sort((a, b) => a.inicio - b.inicio);
  });
  readonly filasPico = FILAS_PICO;

  // Rótulos del eje X: primera ventana, la central y la última.
  readonly rotulos = computed(() => {
    const v = this.ventanas();
    return v.length ? [v[0], v[Math.floor(v.length / 2)], v[v.length - 1]].map(x => this.fecha(x.inicio)) : [];
  });

  // Construye un rectángulo por ventana con n > 0. Y crece hacia abajo en SVG; por eso se resta del techo.
  private trazo(incluir: (v: Ventana) => boolean): string {
    const t = this.techo();
    return this.ventanas().map((v, i) => v.n > 0 && incluir(v)
      ? `M${i + HUECO} ${t}V${t - v.n}H${i + 1 - HUECO}V${t}Z` : '').join('');
  }

  // Convierte la posición del ratón en el número de ventana.
  mover(evento: PointerEvent): void {
    const caja = (evento.currentTarget as Element).getBoundingClientRect();
    const total = this.ventanas().length;
    const i = Math.floor((evento.clientX - caja.left) / caja.width * total);
    this.seleccion.set(Math.max(0, Math.min(total - 1, i)));
  }

  // Fecha y hora en UTC, sin segundos.
  fecha(ms: number): string {
    return new Date(ms).toLocaleString('es-ES', { timeZone: 'UTC', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  private describir(v: Ventana): string {
    return `${this.fecha(v.inicio)} UTC, ${v.n.toLocaleString('es-ES')} ${v.n === 1 ? 'terremoto' : 'terremotos'}${v.parcial ? ' (ventana parcial)' : ''}`;
  }
}
