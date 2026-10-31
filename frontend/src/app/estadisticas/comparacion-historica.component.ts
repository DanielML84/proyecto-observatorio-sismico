// Comparación con 2025. Todas las cifras vienen de la API; aquí solo se presentan
// y se avisa de cuándo un porcentaje no significa lo que parece.
import { Component, computed, input } from '@angular/core';
import type { ComparacionHistorica, Periodo } from '../api.service';

const INICIO_2025 = Date.UTC(2025, 0, 1);
const FIN_2025 = Date.UTC(2026, 0, 1);
const BASE_MINIMA = 1;                                 // criterio propio: esperar menos de 1 terremoto no da un % útil

// Número en español. ND si falta.
const cifra = (valor: number | null, decimales = 0): string =>
  valor === null ? 'ND' : valor.toLocaleString('es-ES', { maximumFractionDigits: decimales });

@Component({
  selector: 'app-comparacion-historica', standalone: true,
  templateUrl: './comparacion-historica.component.html', styleUrl: './comparacion-historica.component.css'
})
export class ComparacionHistoricaComponent {
  readonly datos = input.required<ComparacionHistorica>();
  readonly periodo = input.required<Periodo & { horas: number }>();
  readonly generated = input.required<number>();
  readonly minMag = input.required<number | null>();    // filtro pedido, para explicar si difiere del comparado
  readonly total = input.required<number>();            // recuento con los filtros pedidos

  private readonly inicio = computed(() => new Date(this.periodo().start).getTime());
  private readonly fin = computed(() => new Date(this.periodo().end).getTime());

  // «>= 4.0» -> 4: el número con el que la API ha comparado de verdad.
  readonly magnitud = computed(() => Number(this.datos().filtro_magnitud.replace('>=', '')));
  readonly magnitudTexto = computed(() => cifra(this.magnitud(), 2));
  // La comparación usa M≥4 como mínimo: si se pidió menos, su recuento puede no coincidir con el total de arriba.
  readonly filtroElevado = computed(() => (this.minMag() ?? -Infinity) < this.magnitud() && this.datos().reciente !== this.total());

  // Los días de 2025 son periodos de 24 h: solo con un periodo igual se pueden poner en la misma escala.
  readonly es24h = computed(() => Math.abs(this.periodo().horas - 24) < 0.01);

  // El periodo cae dentro de 2025: se compara con un año que ya lo contiene.
  readonly solapa2025 = computed(() => this.inicio() < FIN_2025 && this.fin() > INICIO_2025);
  // Fecha desde la que hay datos del feed, según la API. null = aún no hay ninguna ingesta correcta.
  private readonly cobertura = computed(() => {
    const desde = this.datos().cobertura_feed_desde;
    return desde === null ? null : new Date(desde).getTime();
  });
  // La API dice que el periodo no está cubierto y es porque empieza antes de los datos del feed
  // (periodo_cubierto también es false si solo termina en el futuro: de eso se avisa aparte).
  readonly fueraDeCobertura = computed(() => {
    const desde = this.cobertura();
    return !this.datos().periodo_cubierto && (desde === null || this.inicio() < desde);
  });
  readonly coberturaTexto = computed(() => {
    const desde = this.cobertura();
    return desde === null ? 'ND' : `${new Date(desde).toLocaleString('es-ES', { timeZone: 'UTC' })} UTC`;
  });
  // Termina en el futuro: el esperado incluye días que aún no han ocurrido.
  readonly periodoFuturo = computed(() => this.fin() > this.generated());
  // Hay porcentaje, pero sobre una base tan pequeña que un solo terremoto lo cambia por completo.
  readonly baseMuyPequena = computed(() => this.datos().variacion_pct !== null && this.datos().esperado_en_periodo < BASE_MINIMA);

  readonly reciente = computed(() => cifra(this.datos().reciente));
  // Un valor positivo muy pequeño llega de la API redondeado a 0: se escribe <0,01 para no decir que era 0.
  private pequeno(valor: number): string {
    return valor === 0 && this.datos().historico_2025_total > 0 ? '<0,01' : cifra(valor, 2);
  }
  readonly esperado = computed(() => this.pequeno(this.datos().esperado_en_periodo));
  readonly variacion = computed(() => {
    const v = this.datos().variacion_pct;
    return v === null ? 'ND' : `${v.toLocaleString('es-ES', { maximumFractionDigits: 1, signDisplay: 'exceptZero' })} %`;
  });
  readonly diferencia = computed(() => this.datos().diferencia.toLocaleString('es-ES', { maximumFractionDigits: 2, signDisplay: 'exceptZero' }));
  readonly historico = computed(() => cifra(this.datos().historico_2025_total));
  readonly media = computed(() => this.pequeno(this.datos().media_diaria_2025));
  readonly mediana = computed(() => cifra(this.datos().dias_2025.mediana));
  readonly p10 = computed(() => cifra(this.datos().dias_2025.p10));
  readonly p90 = computed(() => cifra(this.datos().dias_2025.p90));
  readonly pctDias = computed(() => this.datos().dias_2025.pct_dias_con_recuento_menor_o_igual);
  readonly pctDiasTexto = computed(() => cifra(this.pctDias(), 1));

  // Escala común de la figura: de 0 hasta algo más que el mayor valor, para que nada toque el borde.
  readonly maximo = computed(() => {
    const d = this.datos();
    return Math.max(1, Math.ceil(Math.max(d.reciente, d.media_diaria_2025, d.dias_2025.p90 ?? 0) * 1.1));
  });

  // Posición en % sobre esa escala.
  posicion(valor: number | null): number { return (valor ?? 0) / this.maximo() * 100; }
}
