# Comprobación en Power BI mediante Edge

El 10 de noviembre de 2026 (hora de Lima) abrí el laboratorio virtual de DataCamp en Edge y cargué el modelo inicial `1_1_data_check_solution.pbix`. Ejecuté las consultas de `validacion_motor.dax` en la vista de consultas DAX. No apliqué las medidas de consulta al modelo persistente.

| Comprobación | Resultado de Power BI | Contraste con Python |
|---|---:|---|
| Clientes distintos | 6 687 | Coincide |
| Bajas | 1 796 | Coincide |
| Tasa global, mostrada con dos decimales | 26,86 % | Coincide |
| Filas menos clientes distintos | 0 | Coincide |
| Bajas con motivo vacío | 27 | Coincide |
| Mensual: clientes / bajas / tasa | 3 411 / 1 579 / 46,29 % | Coincide |
| Un año: clientes / bajas / tasa | 1 479 / 167 / 11,29 % | Coincide |
| Dos años: clientes / bajas / tasa | 1 797 / 50 / 2,78 % | Coincide |

## Hallazgo durante la prueba

El primer control utilizó `ISBLANK` y no encontró las 27 bajas sin motivo: el modelo inicial conservaba cadenas vacías. Cambié el filtro a `[Churn Reason] = ""`, que en DAX también contempla la equivalencia con BLANK en esta comparación. La consulta corregida devolvió 27. Power Query de la plantilla propia ya contempla tanto `null` como texto vacío después de `Text.Trim`.

`FORMAT` se usa solo para leer porcentajes con dos decimales en esta consulta. Las medidas del informe conservan valores numéricos y su formato porcentual.

## Alcance y persistencia

Power BI mostró ejecución correcta. Guardé una copia denominada `Databel_validacion_DAX.pbix` dentro del laboratorio; la barra de título confirmó el nombre y la hora de guardado. Este es un archivo remoto de comprobación basado en el modelo inicial, no la plantilla propia de cuatro páginas. La consulta y sus resultados están conservados también en los archivos locales del proyecto; no se depende de que DataCamp retenga la máquina virtual indefinidamente.

Las capturas se mantienen en `evidence/` como evidencia local. La compilación del PBIT, el cálculo sobre el CSV y esta ejecución del motor son comprobaciones distintas. Sigue pendiente abrir la plantilla propia y revisar sus filtros y visuales. El progreso del caso ya estaba completo antes de esta prueba y no se atribuye una nueva aprobación a la adaptación.
