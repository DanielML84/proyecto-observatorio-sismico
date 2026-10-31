import { Component, OnDestroy, inject, signal } from '@angular/core';
import { LeafletDirective } from '@bluehalo/ngx-leaflet';
import * as L from 'leaflet';
import type { FeatureCollection } from 'geojson';
import { ApiService, Config, Eventos, FILTROS_VACIOS, Filtros, MetadatosEventos, SIN_PAIS } from './api.service';
import { ESTADO_INICIAL, EstadoSistema, EstadoSistemaComponent } from './estado-sistema/estado-sistema.component';
import { FiltrosComponent, PaisOpcion } from './filtros/filtros.component';

@Component({
  selector: 'app-root', standalone: true, imports: [LeafletDirective, EstadoSistemaComponent, FiltrosComponent],
  templateUrl: './app.component.html', styleUrl: './app.component.css'
})
export class AppComponent implements OnDestroy {
  // Un único objeto con el estado: al cambiarlo, el componente de estado se repinta solo.
  readonly estado = signal<EstadoSistema>(ESTADO_INICIAL);
  readonly filtros = signal<Filtros>(FILTROS_VACIOS);   // filtros que usa cada consulta
  // Opciones del desplegable. «Sin país asignado» no está en el catálogo: existe aunque este no cargue.
  readonly paises = signal<PaisOpcion[]>([{ id: SIN_PAIS, nombre: 'Sin país asignado' }]);
  readonly cargando = signal(false);                    // hay una consulta en marcha
  readonly options: L.MapOptions = { center: L.latLng(18, 0), zoom: 2, minZoom: 2, maxZoom: 8, preferCanvas: true, worldCopyJump: false };
  // Angular entrega aquí la única instancia del servicio.
  private api = inject(ApiService);
  private map?: L.Map;
  private events = L.layerGroup();
  private timer?: ReturnType<typeof setTimeout>;
  private destroyed = false;
  private config?: Config;
  private pendiente = false;                            // han cambiado los filtros durante una consulta

  async onMapReady(map: L.Map): Promise<void> {
    this.map = map;
    const base = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, noWrap: true, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    const borders = L.geoJSON(undefined, { style: { color: '#334155', weight: 1, fill: false },
      onEachFeature: (feature, layer) => {
        const name = document.createElement('span');
        name.textContent = feature.properties?.NAME_ES ?? feature.properties?.ADMIN ?? 'Sin nombre';
        layer.bindTooltip(name);
      }
    }).addTo(map);
    this.events.addTo(map);
    L.control.layers({ 'OpenStreetMap': base }, { 'Países (Natural Earth)': borders, 'Terremotos': this.events }).addTo(map);
    map.attributionControl.addAttribution('Fronteras: Natural Earth · Datos reales: USGS');
    try {
      const catalogo = await this.api.leerJson<FeatureCollection>('datos/paises.geojson');
      borders.addData(catalogo);
      this.cargarPaises(catalogo);                      // el mismo archivo da las fronteras y la lista de países
      this.actualizar({ catalogo: 'Catálogo de países cargado' });
    } catch { this.actualizar({ catalogo: 'No se pudo cargar el catálogo de países' }); }
    if (this.destroyed) return;
    try {
      const config = await this.api.leerConfig();
      this.config = config;
      this.actualizar({ modo: config.mode });
      await this.refresh(config);
    } catch { this.actualizar({ errorConfig: true }); }
  }

  // El formulario ha enviado filtros nuevos: consultar ya, sin esperar al siguiente refresco.
  aplicarFiltros(filtros: Filtros): void {
    this.filtros.set(filtros);
    if (!this.config) return;
    // Si hay una consulta en marcha, no se lanza otra: se repetirá al terminar (sin peticiones solapadas).
    if (this.cargando()) { this.pendiente = true; return; }
    clearTimeout(this.timer);                           // la consulta de ahora sustituye al refresco programado
    void this.refresh(this.config);
  }

  // Cambia solo los campos indicados y deja el resto del estado como estaba.
  private actualizar(cambios: Partial<EstadoSistema>): void {
    this.estado.update(actual => ({ ...actual, ...cambios }));
  }

  private async refresh(config: Config): Promise<void> {
    this.cargando.set(true);
    const filtros = this.filtros();                     // la misma copia para todas las llamadas de este ciclo
    // allSettled espera a todas las llamadas y no se detiene si una falla; así sabemos cuál ha fallado.
    const [eventos, salud] = await Promise.allSettled([
      this.api.eventos(config, filtros),
      config.mode === 'api' ? this.api.salud(config) : null   // el modo demo no tiene backend al que preguntar
    ]);
    if (this.destroyed) return;
    this.cargando.set(false);
    // null si /api/salud falló o si estamos en demo.
    const lecturaSalud = salud.status === 'fulfilled' ? salud.value : null;
    const saludRecibida = { falloSalud: salud.status === 'rejected', desactualizados: lecturaSalud?.datos_desactualizados ?? null };
    try {
      if (this.pendiente) return;                       // estos datos ya no son los pedidos: no se pintan
      if (eventos.status === 'rejected') throw eventos.reason;
      const data = eventos.value;
      const { count, omitted } = this.pintar(data);
      const meta = data.metadata;
      this.actualizar({
        ...saludRecibida, falloApi: false, count, omitted,
        ultimoAcceso: Date.now(),                 // solo aquí: es la hora de la última lectura CORRECTA
        generated: meta?.generated ?? null,
        // /api/salud es lo más reciente; si no respondió, vale el dato que venía con los eventos.
        lastIngestion: lecturaSalud?.last_ingestion ?? meta?.last_ingestion ?? null,
        periodo: meta?.periodo ?? null,
        filtrosLectura: this.textoFiltros(meta),
        total: meta?.total ?? null,
        truncated: meta?.truncated === true
      });
    } catch {
      // Fallo: NO se toca ni el mapa ni las fechas; siguen describiendo la última lectura buena.
      this.actualizar({ ...saludRecibida, falloApi: true });
    } finally {
      if (this.pendiente) {
        // Los filtros cambiaron durante la consulta: repetirla ya con los nuevos.
        this.pendiente = false;
        void this.refresh(config);
      } else if (!this.destroyed && config.mode === 'api') {
        // El siguiente refresco se programa al terminar este, así nunca hay dos a la vez.
        this.timer = setTimeout(() => void this.refresh(config), Math.max(30000, Number(config.refreshMs) || 60000));
      }
    }
  }

  // Convierte el catálogo en las opciones del desplegable: «Sin país asignado» primero y el resto por nombre.
  private cargarPaises(catalogo: FeatureCollection): void {
    const paises: PaisOpcion[] = catalogo.features.map(f => ({ id: f.properties?.['ADM0_A3'], nombre: f.properties?.['NAME_ES'] }));
    paises.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));   // 'es': la Á va con la A y la Ñ tras la N
    this.paises.update(actuales => [...actuales, ...paises]);        // se añaden detrás de «Sin país asignado»
  }

  // Describe los filtros que la API dice haber aplicado (no los del formulario, que pueden ser más nuevos).
  private textoFiltros(meta?: MetadatosEventos): string | null {
    if (!meta?.filtros) return null;                    // el GeoJSON de demo no trae filtros
    const { min_mag, country_id } = meta.filtros;
    const partes = [];
    if (min_mag !== null) partes.push(`Magnitud ≥ ${min_mag}`);
    if (country_id) partes.push(`País: ${this.paises().find(p => p.id === country_id)?.nombre ?? country_id}`);
    return partes.length ? partes.join(' · ') : 'Sin filtro de magnitud ni de país';
  }

  // Dibuja los terremotos y devuelve cuántos ha dibujado y cuántos ha omitido.
  private pintar(data: Eventos): { count: number; omitted: number } {
    // Construir primero la nueva capa: si falla, conservar la anterior.
    const next = L.layerGroup(); let omitted = 0; let count = 0;
    for (const feature of data.features) {
      const p = feature.properties;
      const c = feature.geometry?.type === 'Point' ? feature.geometry.coordinates : [];
      const [lon, lat, depth] = c;
      if (!p || !Number.isFinite(lon) || !Number.isFinite(lat) || Math.abs(lon) > 180 || Math.abs(lat) > 90) { omitted++; continue; }
      const magnitude = typeof p.mag === 'number' && Number.isFinite(p.mag) ? p.mag : null;
      const depthOk = typeof depth === 'number' && Number.isFinite(depth);
      const color = !depthOk ? '#64748b' : depth < 70 ? '#e8a317' : depth < 300 ? '#e35b37' : '#7b3fb6';
      const popup = document.createElement('div');
      popup.textContent = `${p.place ?? 'Sin descripción'}\nMagnitud: ${magnitude ?? 'ND'}\nProfundidad: ${depthOk ? depth + ' km' : 'ND'}\nFecha UTC: ${this.date(p.time)}\nPaís: ${p.country_name ?? 'Sin país asignado'}\nID: ${feature.id ?? 'ND'}`;
      L.circleMarker([lat, lon], { radius: magnitude === null ? 4 : Math.max(3, Math.min(18, 3 + (magnitude + 1) * 2)), color, fillColor: color, fillOpacity: .75, weight: 1 }).bindPopup(popup).addTo(next);
      count++;
    }
    this.events.clearLayers(); this.events.addLayer(next);
    return { count, omitted };
  }

  private date(value: unknown): string {
    if (typeof value !== 'number' || !Number.isFinite(value)) return 'ND';
    const d = new Date(value); return Number.isNaN(d.getTime()) ? 'ND' : d.toISOString();
  }
  // Las peticiones en curso las cancela ApiService.ngOnDestroy.
  ngOnDestroy(): void { this.destroyed = true; clearTimeout(this.timer); }
}
