// Bloque de estadísticas: prepara los datos de la API para los gráficos. No calcula recuentos:
// todos vienen de la API, nunca de la muestra de eventos, que puede estar truncada (encargo, punto 8).
import { Component, computed, input } from '@angular/core';
import type { Estadisticas } from '../api.service';
import { FilaBarra, GraficoBarrasComponent } from './grafico-barras.component';
import { GraficoHorasComponent } from './grafico-horas.component';

// Clases de la API en orden de profundidad, con los mismos colores que el mapa (la API no garantiza el orden).
const CLASES_PROFUNDIDAD: { clase: string; color: string }[] = [
  { clase: 'negativa (<0 km)', color: '#e8a317' },        // en el mapa, cualquier profundidad < 70 km es amarilla
  { clase: 'superficial (0-70 km)', color: '#e8a317' },
  { clase: 'intermedia (70-300 km)', color: '#e35b37' },
  { clase: 'profunda (>=300 km)', color: '#7b3fb6' }
];

const decimal = (valor: number): string => valor.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 });

@Component({
  selector: 'app-estadisticas', standalone: true, imports: [GraficoBarrasComponent, GraficoHorasComponent],
  templateUrl: './estadisticas.component.html', styleUrl: './estadisticas.component.css'
})
export class EstadisticasComponent {
  readonly datos = input.required<Estadisticas | null>();  // última lectura correcta
  readonly antiguas = input(false);                        // el último intento de actualizarlas ha fallado
  readonly filtrosTexto = input<string | null>(null);      // filtros con los que se calcularon
  readonly truncado = input(false);                        // la lista de eventos del mapa está truncada
  readonly cargando = input(false);                        // hay una consulta en marcha

  readonly paises = computed<FilaBarra[]>(() => (this.datos()?.por_pais ?? []).map(p => ({ etiqueta: p.nombre, n: p.n })));
  readonly subregiones = computed<FilaBarra[]>(() => (this.datos()?.por_subregion ?? []).map(s => ({ etiqueta: s.subregion, n: s.n })));

  // La API solo envía los tramos con eventos. Se rellenan los huecos con 0: un tramo vacío también es un dato.
  readonly magnitudes = computed<FilaBarra[]>(() => {
    const d = this.datos()?.distribucion_magnitud;
    if (!d || d.tramos.length === 0) return [];
    // Se trabaja en «número de tramo» (enteros) para evitar errores de redondeo al sumar 0,5.
    const recuento = new Map(d.tramos.map(t => [Math.round(t.desde / d.tramo), t.n]));
    const claves = [...recuento.keys()];
    const filas: FilaBarra[] = [];
    for (let k = Math.min(...claves); k <= Math.max(...claves); k++) {
      filas.push({ etiqueta: `${decimal(k * d.tramo)} a <${decimal((k + 1) * d.tramo)}`, n: recuento.get(k) ?? 0 });
    }
    return filas;
  });

  // Siempre las cuatro clases y en orden, aunque alguna tenga 0.
  readonly profundidades = computed<FilaBarra[]>(() => {
    const clases = this.datos()?.distribucion_profundidad.clases ?? [];
    return CLASES_PROFUNDIDAD.map(c => ({ etiqueta: c.clase, n: clases.find(x => x.clase === c.clase)?.n ?? 0, color: c.color }));
  });

  // Fecha y hora en UTC, con la zona escrita.
  utc(valor: string | number): string {
    return `${new Date(valor).toLocaleString('es-ES', { timeZone: 'UTC' })} UTC`;
  }

  cifra(n: number): string { return n.toLocaleString('es-ES'); }
}
