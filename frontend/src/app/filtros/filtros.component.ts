// Formulario de filtros. Valida lo escrito y avisa al componente padre; no llama a la API.
import { Component, input, output, signal } from '@angular/core';
import { FILTROS_VACIOS, Filtros } from '../api.service';

// Una opción del desplegable de país.
export type PaisOpcion = { id: string; nombre: string };

@Component({
  selector: 'app-filtros', standalone: true,
  templateUrl: './filtros.component.html', styleUrl: './filtros.component.css'
})
export class FiltrosComponent {
  readonly paises = input.required<PaisOpcion[]>();   // opciones del desplegable
  readonly aplicados = input.required<Filtros>();     // filtros en uso, para marcar el país elegido
  readonly cargando = input(false);                   // hay una consulta en marcha
  readonly aplicar = output<Filtros>();               // se emite cuando hay filtros válidos
  readonly error = signal<string | null>(null);       // mensaje de validación

  // El navegador da «2025-07-29T00:00», sin zona. Añadir Z indica que esa hora es UTC.
  private aIso(valor: string): string | null {
    return valor ? new Date(`${valor}Z`).toISOString() : null;
  }

  // Lee los campos al pulsar «Aplicar». Se usan campos HTML porque @angular/forms no es dependencia del proyecto.
  enviar(evento: Event, inicio: HTMLInputElement, fin: HTMLInputElement, magnitud: HTMLInputElement, pais: HTMLSelectElement): void {
    evento.preventDefault();                          // sin esto, el navegador recargaría la página
    // Texto no numérico en un campo number: el navegador lo marca como badInput.
    if (magnitud.validity.badInput) { this.error.set('La magnitud mínima debe ser un número.'); return; }
    const start = this.aIso(inicio.value);
    const end = this.aIso(fin.value);
    // La API respondería 200 con 0 eventos: parecería que no hubo terremotos, así que se rechaza aquí.
    if (start && end && start >= end) { this.error.set('La fecha de inicio debe ser anterior a la de fin.'); return; }
    this.error.set(null);
    this.aplicar.emit({
      start, end,
      min_mag: magnitud.value === '' ? null : magnitud.valueAsNumber,
      country_id: pais.value || null                  // '' = «Todos los países»
    });
  }

  // Vacía el formulario y vuelve a las últimas 24 h.
  limpiar(formulario: HTMLFormElement): void {
    formulario.reset();
    this.error.set(null);
    this.aplicar.emit(FILTROS_VACIOS);
  }
}
