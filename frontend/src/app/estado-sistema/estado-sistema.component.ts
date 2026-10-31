// Componente «tonto»: recibe el estado ya calculado y lo muestra. No llama a la API.
import { Component, input } from '@angular/core';
import type { Periodo } from '../api.service';

// Todo lo que el panel necesita contar sobre el estado del sistema (enunciado §8, punto 6).
export type EstadoSistema = {
  modo: 'cargando' | 'demo' | 'api';
  errorConfig: boolean;             // config.json ilegible o con un modo inválido
  falloApi: boolean;                // el ÚLTIMO intento de leer eventos ha fallado
  falloSalud: boolean;              // no se ha podido comprobar /api/salud
  desactualizados: boolean | null;  // null = no se sabe (demo, o /api/salud no respondió)
  ultimoAcceso: number | null;      // reloj del navegador en la última lectura correcta
  generated: number | null;         // cuándo generó la API la respuesta que se está mostrando
  lastIngestion: number | null;     // última consulta correcta a USGS
  periodo: Periodo | null;          // periodo de la última lectura correcta
  count: number;                    // eventos dibujados
  omitted: number;                  // eventos descartados por coordenadas inválidas
  total: number | null;             // eventos que cumplen los filtros en la API
  truncated: boolean;               // la API no ha enviado todos los eventos
  catalogo: string;                 // estado del catálogo de países
};

// Valores antes de la primera lectura: nada se da por conocido.
export const ESTADO_INICIAL: EstadoSistema = {
  modo: 'cargando', errorConfig: false, falloApi: false, falloSalud: false, desactualizados: null,
  ultimoAcceso: null, generated: null, lastIngestion: null, periodo: null,
  count: 0, omitted: 0, total: null, truncated: false, catalogo: 'Cargando catálogo'
};

@Component({
  selector: 'app-estado-sistema', standalone: true,
  templateUrl: './estado-sistema.component.html', styleUrl: './estado-sistema.component.css'
})
export class EstadoSistemaComponent {
  // input.required: el componente padre está obligado a pasar el estado.
  readonly estado = input.required<EstadoSistema>();

  // Hora local del navegador (el encargo la pide así para el último acceso).
  local(valor: number | null): string {
    return valor === null ? 'Sin lectura' : new Date(valor).toLocaleString('es-ES');
  }

  // Hora UTC, en el mismo formato, con la zona escrita para que no se confunda con la local.
  utc(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined) return 'ND';
    const fecha = new Date(valor);
    return Number.isNaN(fecha.getTime()) ? 'ND' : `${fecha.toLocaleString('es-ES', { timeZone: 'UTC' })} UTC`;
  }
}
