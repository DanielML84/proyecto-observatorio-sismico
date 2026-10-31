import { Component, OnDestroy, inject, signal } from '@angular/core';
import { LeafletDirective } from '@bluehalo/ngx-leaflet';
import * as L from 'leaflet';
import type { FeatureCollection } from 'geojson';
import { ApiService, Config, Eventos } from './api.service';
import { ESTADO_INICIAL, EstadoSistema, EstadoSistemaComponent } from './estado-sistema/estado-sistema.component';

@Component({
  selector: 'app-root', standalone: true, imports: [LeafletDirective, EstadoSistemaComponent],
  templateUrl: './app.component.html', styleUrl: './app.component.css'
})
export class AppComponent implements OnDestroy {
  // Un único objeto con el estado: al cambiarlo, el componente de estado se repinta solo.
  readonly estado = signal<EstadoSistema>(ESTADO_INICIAL);
  readonly options: L.MapOptions = { center: L.latLng(18, 0), zoom: 2, minZoom: 2, maxZoom: 8, preferCanvas: true, worldCopyJump: false };
  // Angular entrega aquí la única instancia del servicio.
  private api = inject(ApiService);
  private map?: L.Map;
  private events = L.layerGroup();
  private timer?: ReturnType<typeof setTimeout>;
  private destroyed = false;

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
      borders.addData(await this.api.leerJson<FeatureCollection>('datos/paises.geojson'));
      this.actualizar({ catalogo: 'Catálogo de países cargado' });
    } catch { this.actualizar({ catalogo: 'No se pudo cargar el catálogo de países' }); }
    if (this.destroyed) return;
    try {
      const config = await this.api.leerConfig();
      this.actualizar({ modo: config.mode });
      await this.refresh(config);
    } catch { this.actualizar({ errorConfig: true }); }
  }

  // Cambia solo los campos indicados y deja el resto del estado como estaba.
  private actualizar(cambios: Partial<EstadoSistema>): void {
    this.estado.update(actual => ({ ...actual, ...cambios }));
  }

  private async refresh(config: Config): Promise<void> {
    // allSettled espera a las dos llamadas y no se detiene si una falla; así sabemos cuál ha fallado.
    const [eventos, salud] = await Promise.allSettled([
      this.api.eventos(config),
      config.mode === 'api' ? this.api.salud(config) : null   // el modo demo no tiene backend al que preguntar
    ]);
    if (this.destroyed) return;
    // null si /api/salud falló o si estamos en demo.
    const lecturaSalud = salud.status === 'fulfilled' ? salud.value : null;
    const saludRecibida = { falloSalud: salud.status === 'rejected', desactualizados: lecturaSalud?.datos_desactualizados ?? null };
    try {
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
        total: meta?.total ?? null,
        truncated: meta?.truncated === true
      });
    } catch {
      // Fallo: NO se toca ni el mapa ni las fechas; siguen describiendo la última lectura buena.
      this.actualizar({ ...saludRecibida, falloApi: true });
    } finally {
      // El siguiente refresco se programa al terminar este, así nunca hay dos a la vez.
      if (!this.destroyed && config.mode === 'api') this.timer = setTimeout(() => void this.refresh(config), Math.max(30000, Number(config.refreshMs) || 60000));
    }
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
