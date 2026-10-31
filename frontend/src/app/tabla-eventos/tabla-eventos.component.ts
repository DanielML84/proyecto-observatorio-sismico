// Tabla de terremotos: alternativa accesible al mapa y al color (enunciado §8).
// Recibe los mismos eventos que dibuja el mapa, así que no hace ninguna petición a la API.
import { Component, computed, input, linkedSignal, signal } from '@angular/core';
import type { Feature, Point } from 'geojson';
import type { Filtros, PropiedadesEvento } from '../api.service';
import type { EstadoSistema } from '../estado-sistema/estado-sistema.component';

// Una fila ya preparada para mostrar y ordenar. null = dato no disponible.
type Fila = { id: string; fecha: number | null; magnitud: number | null; profundidad: number | null; pais: string; lugar: string };
type Columna = 'fecha' | 'magnitud' | 'profundidad' | 'pais' | 'lugar';
type Direccion = 'asc' | 'desc';

const FILAS_POR_PAGINA = 50;                            // sin paginar, el navegador tendría que pintar hasta 5.000 filas

// Cabeceras de la tabla, con el orden que se aplica al pulsar cada una por primera vez.
const COLUMNAS: { id: Columna; titulo: string; inicial: Direccion }[] = [
  { id: 'fecha', titulo: 'Fecha (UTC)', inicial: 'desc' },
  { id: 'magnitud', titulo: 'Magnitud', inicial: 'desc' },
  { id: 'profundidad', titulo: 'Profundidad (km)', inicial: 'desc' },
  { id: 'pais', titulo: 'País', inicial: 'asc' },
  { id: 'lugar', titulo: 'Lugar', inicial: 'asc' }
];

// Compara textos con las reglas del español (la Á va con la A). Se crea una vez porque es más rápido.
const COMPARADOR_TEXTO = new Intl.Collator('es');

// Devuelve el número si es válido; si no, null.
const numero = (valor: unknown): number | null => typeof valor === 'number' && Number.isFinite(valor) ? valor : null;

@Component({
  selector: 'app-tabla-eventos', standalone: true,
  templateUrl: './tabla-eventos.component.html', styleUrl: './tabla-eventos.component.css'
})
export class TablaEventosComponent {
  readonly eventos = input.required<Feature<Point, PropiedadesEvento>[]>();  // los mismos que el mapa
  readonly estado = input.required<EstadoSistema>();                         // para avisar de datos antiguos o truncados
  readonly filtros = input.required<Filtros>();                              // si cambian, se vuelve a la página 1

  readonly columnas = COLUMNAS;
  readonly columna = signal<Columna>('fecha');          // por defecto: los más recientes primero
  readonly direccion = signal<Direccion>('desc');
  // linkedSignal: guarda la página elegida, pero vuelve a 1 cuando cambian los filtros.
  private readonly paginaPedida = linkedSignal<Filtros, number>({ source: this.filtros, computation: () => 1 });

  // Convierte cada terremoto en una fila.
  private readonly filas = computed<Fila[]>(() => this.eventos().map((evento, i) => {
    const p = evento.properties;
    return {
      id: String(evento.id ?? i),                       // la posición evita un id repetido si faltara
      fecha: numero(p?.time),
      magnitud: numero(p?.mag),
      profundidad: numero(evento.geometry?.coordinates?.[2]),
      pais: p?.country_name ?? 'Sin país asignado',
      lugar: p?.place ?? 'Sin descripción'
    };
  }));

  // Copia ordenada. Solo se recalcula si cambian las filas, la columna o la dirección.
  private readonly ordenadas = computed(() => {
    const columna = this.columna();
    const signo = this.direccion() === 'asc' ? 1 : -1;
    return [...this.filas()].sort((a, b) => {
      const va = a[columna];
      const vb = b[columna];
      // Los datos que faltan van siempre al final, sea cual sea la dirección.
      if (va === null || vb === null) return va === vb ? 0 : va === null ? 1 : -1;
      return signo * (typeof va === 'string' ? COMPARADOR_TEXTO.compare(va, vb as string) : va - (vb as number));
    });
  });

  readonly totalFilas = computed(() => this.filas().length);
  readonly totalPaginas = computed(() => Math.max(1, Math.ceil(this.totalFilas() / FILAS_POR_PAGINA)));
  // Si un refresco deja menos filas, la página pedida podría no existir: se limita a la última.
  readonly pagina = computed(() => Math.min(this.paginaPedida(), this.totalPaginas()));
  // Solo las filas de la página actual llegan al HTML.
  readonly visibles = computed(() => {
    const desde = (this.pagina() - 1) * FILAS_POR_PAGINA;
    return this.ordenadas().slice(desde, desde + FILAS_POR_PAGINA);
  });
  // Nombre de la columna activa, para contar el orden con palabras y no solo con una flecha.
  readonly tituloOrden = computed(() => COLUMNAS.find(c => c.id === this.columna())?.titulo ?? '');

  // Primera pulsación en una columna: su orden inicial. Segunda: invierte el orden.
  ordenar(columna: (typeof COLUMNAS)[number]): void {
    if (this.columna() === columna.id) {
      this.direccion.update(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      this.columna.set(columna.id);
      this.direccion.set(columna.inicial);
    }
    this.paginaPedida.set(1);                           // con otro orden, lo útil es volver al principio
  }

  // Avanza o retrocede una página sin salirse de los límites.
  cambiarPagina(salto: number): void {
    this.paginaPedida.set(Math.max(1, Math.min(this.totalPaginas(), this.pagina() + salto)));
  }

  // Valor de aria-sort: así un lector de pantalla anuncia cómo está ordenada la columna.
  ariaSort(columna: Columna): 'ascending' | 'descending' | 'none' {
    if (this.columna() !== columna) return 'none';
    return this.direccion() === 'asc' ? 'ascending' : 'descending';
  }

  // Fecha en UTC. La zona va en la cabecera de la columna.
  fecha(valor: number | null): string {
    return valor === null ? 'ND' : new Date(valor).toLocaleString('es-ES', { timeZone: 'UTC' });
  }

  // Número con coma decimal y dos decimales como máximo; «ND» si falta.
  cifra(valor: number | null): string {
    return valor === null ? 'ND' : valor.toLocaleString('es-ES', { maximumFractionDigits: 2 });
  }

  // Hora local de la última lectura correcta, igual que en el bloque de estado.
  local(valor: number | null): string {
    return valor === null ? 'ND' : new Date(valor).toLocaleString('es-ES');
  }
}
