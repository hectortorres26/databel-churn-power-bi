# Rediseño visual de Databel

Revisión del 11 de noviembre de 2026. El objetivo es facilitar la lectura durante una presentación y la comparación entre segmentos. El modelo, el CSV y las nueve medidas DAX se conservan.

## Qué necesitaba mejorar

La versión anterior usaba un solo color para tasas y volúmenes, presentaba muchos gráficos de barras similares y dedicaba bastante espacio a notas. La comparación geográfica separaba la tasa de su número de clientes; los motivos largos requerían recorrer una barra de desplazamiento con poco contexto. Los indicadores de las páginas de detalle eran escasos.

## Decisiones de diseño

| Elemento | Cambio | Propósito |
|---|---|---|
| Lienzo | 1440 × 900, cuatro páginas con márgenes y cabeceras comunes | Mantener una lectura consistente |
| Fondo | Marfil suave `#F5F4F0`; tarjetas blancas | Separar bloques sin recargar la página |
| Jerarquía | Azul oscuro `#172F43`, títulos de 28 pt y cifras de 38 pt | Dar prioridad al mensaje y a los indicadores |
| Tipografía | Segoe UI; tamaño y peso según la función | Favorecer la lectura con una familia disponible en Windows |
| Volumen | Azul `#24778A` | Identificar recuentos de clientes y bajas |
| Abandono | Naranja oscuro `#BC5138` | Diferenciar tasas y principales indicadores de bajas |
| Retención | Verde `#287966` | Distinguir clientes retenidos |
| Tasas | Escala común desde cero, con margen superior para etiquetas | Evitar que cada gráfico amplifique diferencias de manera distinta |
| Estados | Tabla con clientes, bajas y tasa en la misma fila | Comparar porcentajes junto con sus denominadores |
| Llamadas | Columnas ordenadas de 0 a 5 | Respetar el orden de una variable discreta, sin sugerir una serie temporal |
| Motivos | Categorías en barras y motivos detallados en tabla | Combinar resumen y consulta de textos largos |
| Interacción | Filtros visibles al inicio y un filtro de estado en Segmentos | Reducir el recorrido necesario para explorar |

Las etiquetas explican el significado además del color. No se agregaron mapas, velocímetros ni gráficos decorativos: las barras, columnas y tablas responden a comparaciones concretas. Las notas metodológicas largas permanecen en la documentación; el informe conserva las advertencias esenciales sobre datos ficticios y causalidad.

## Nuevos elementos útiles

- Indicadores de contexto en Segmentos y Contratos y planes.
- Media de llamadas a soporte, tomada de una medida ya validada.
- Tabla geográfica con las 51 categorías y tres indicadores.
- Tabla de motivos que conserva las 21 categorías, incluidos los casos sin información.
- Orden de tabulación por posición y relaciones de filtrado entre los visuales de cada página.

## Reproducción

```powershell
python scripts/diseno_visual.py
python scripts/crear_pbip.py
python scripts/preparar_pruebas_motor.py
```

El primer script modifica solo la capa del informe. La reconstrucción completa con `scripts/construir_informe.py` también usa este diseño. Al volver a generar, se reemplazan las páginas propias; hay que conservar una copia si se han personalizado manualmente.

## Comprobaciones

La validación estructural del CLI oficial terminó con cero errores y cero advertencias. El PBIT se compiló y reextrajo: las cuatro páginas, 46 objetos y campos coinciden con la fuente, sin objetos fuera del lienzo ni solapamientos geométricos. El modelo conserva su huella anterior. Estas comprobaciones no sustituyen la revisión de las vistas nativas y de los filtros del rediseño.

La validación de datos cubre nueve medidas y 13 contextos. Las 14 combinaciones de dimensión y medida, incluidas las tablas, coinciden con pandas. Revisé las cuatro páginas renderizadas por Desktop y comprobé las selecciones mensual, California con mensual, edad de 65 o más y actividad internacional. Después restauré el total sin selecciones: 6 687 clientes, 1 796 bajas y 26,86 % de abandono. No se ensayaron gestos de ratón ni todas las combinaciones posibles.

La revisión visual permitió corregir valores ocultos en las tablas, títulos de tarjetas demasiado largos y etiquetas superiores en las columnas. El PDF conserva las vistas reales de Power BI y es estático. El paquete de entrega contiene PBIP con modelo TMDL, PBIT alternativo y ambos PDF; requiere cargar la fuente al abrirlo en otro equipo.

Referencia de diseño: [recomendaciones de Microsoft para dashboards](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips). El principio aplicado es priorizar información, mantener escalas coherentes y elegir visuales por su utilidad analítica.
