// Servicio: el ÚNICO archivo del panel que sabe hablar con la API.
// Los componentes piden datos aquí y nunca escriben una URL ni un fetch por su cuenta.
import { Injectable, OnDestroy } from '@angular/core';
import type { FeatureCollection, Point } from 'geojson';

// Forma de public/config.json.
export type Config = { mode: 'demo' | 'api'; apiUrl: string; refreshMs: number; skipNgrokWarning: boolean };

// Propiedades de cada terremoto en /api/eventos (backend/src/api.py).
export type PropiedadesEvento = {
  mag: number | null;              // puede faltar: se muestra «ND»
  magType?: string | null;
  place: string;
  time: number;                    // milisegundos Unix
  updated: number;                 // milisegundos Unix
  status?: string;
  country_id?: string | null;      // null = sin país asignado
  country_name?: string | null;
  subregion?: string | null;
};

// Periodo realmente consultado. La API lo devuelve siempre, aunque no se le pida ninguno.
export type Periodo = { start: string; end: string };

// Datos sobre la respuesta, no sobre los terremotos. Son opcionales porque el GeoJSON de demo no trae todos.
export type MetadatosEventos = {
  generated?: number;              // cuándo se generó ESTA respuesta
  last_ingestion?: number | null;  // última consulta correcta a USGS
  mode?: string;
  count?: number;                  // eventos incluidos en esta respuesta
  total?: number;                  // eventos que cumplen los filtros
  truncated?: boolean;             // true = hay más eventos que los incluidos
  periodo?: Periodo;
};

// Una FeatureCollection de GeoJSON con nuestros metadatos añadidos.
export type Eventos = FeatureCollection<Point, PropiedadesEvento> & { metadata?: MetadatosEventos };

// Respuesta de /api/salud cuando la base de datos funciona.
export type Salud = {
  api: string;
  base_datos: string;
  generated: number;
  last_ingestion: number | null;
  segundos_desde_ultima_ingesta: number | null;
  datos_desactualizados: boolean;
};

// providedIn 'root' = Angular crea una sola instancia para toda la aplicación.
@Injectable({ providedIn: 'root' })
export class ApiService implements OnDestroy {
  // Permite cancelar las peticiones en curso cuando se cierra la aplicación.
  private controller = new AbortController();

  // Pide un JSON y falla con un error si la respuesta no es correcta.
  async leerJson<T>(url: string, headers: Record<string, string> = {}): Promise<T> {
    const response = await fetch(url, {
      headers,
      cache: 'no-store',                             // no reutilizar respuestas guardadas por el navegador
      // Se cancela al cerrar la aplicación o a los 15 s (el contrato pide timeout en el frontend).
      signal: AbortSignal.any([this.controller.signal, AbortSignal.timeout(15000)])
    });
    // fetch no falla con un 404 o un 503: hay que comprobarlo a mano.
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json() as Promise<T>;
  }

  // Lee public/config.json y comprueba que el modo es válido.
  async leerConfig(): Promise<Config> {
    const config = await this.leerJson<Config>('config.json');
    if (!['demo', 'api'].includes(config.mode)) throw new Error('Modo inválido');
    return config;
  }

  // Terremotos: en demo, el archivo de ejemplo; en api, nuestro backend (nunca USGS directamente).
  async eventos(config: Config): Promise<Eventos> {
    const url = config.mode === 'demo' ? 'datos/terremotos-demo.geojson' : this.url(config, '/api/eventos');
    const data = await this.leerJson<Eventos>(url, this.cabeceras(config));
    // Si llega otra cosa (por ejemplo, la página HTML de aviso de ngrok), se trata como un fallo.
    if (data.type !== 'FeatureCollection' || !Array.isArray(data.features)) throw new Error('Se esperaba FeatureCollection');
    return data;
  }

  // Estado de la API y de la última ingesta. Un 503 (base de datos caída) llega aquí como error.
  salud(config: Config): Promise<Salud> {
    return this.leerJson<Salud>(this.url(config, '/api/salud'), this.cabeceras(config));
  }

  // Une la URL base y la ruta, tolerando una barra final en config.json.
  private url(config: Config, ruta: string): string {
    return `${config.apiUrl.replace(/\/$/, '')}${ruta}`;
  }

  // La cabecera de ngrok evita su página intermedia; no autentica a nadie (CONTRATO-API).
  private cabeceras(config: Config): Record<string, string> {
    return config.mode === 'api' && config.skipNgrokWarning ? { 'ngrok-skip-browser-warning': '1' } : {};
  }

  // Angular llama a este método al destruir el servicio: cancela lo que siga en curso.
  ngOnDestroy(): void { this.controller.abort(); }
}
