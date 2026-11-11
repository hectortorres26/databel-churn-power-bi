# Validación del dashboard Databel

Revisión del 10 de noviembre de 2026. Separé las pruebas de datos, modelo y presentación para que el estado del proyecto sea verificable.

## Datos y modelo propio

La plantilla inicial de esta adaptación cargó su CSV en Power BI Desktop. La partición figura como `Ready`. Las nueve medidas, las columnas y la expresión Power Query del modelo cargado coinciden con la definición que acompaña a la plantilla revisada. El modelo excluye `Phone Number`.

Ejecuté consultas DAX de solo lectura mediante ADOMD y comparé los resultados con cálculos independientes de pandas. El resultado está en [`output/validacion_motor.json`](../output/validacion_motor.json), que registra también el SHA-256 de la definición del modelo.

| Comprobación | Resultado |
|---|---|
| Clientes / bajas / retenidos | 6 687 / 1 796 / 4 891 |
| Tasa global | 26,8581 % |
| Bajas sin motivo | 27 |
| IDs duplicados | 0 |
| Nueve medidas en 13 contextos de filtro | Todas coinciden con Python |
| Once combinaciones de dimensión y medida de los gráficos | Todas coinciden, categoría por categoría |
| Mismo modelo en fuente y sesión cargada | Correcto |

Los filtros incluyen los tres contratos, dos grupos de edad, California, California con contrato mensual, actividad internacional cruzada con plan, clientes retenidos, una selección sin registros y el total restablecido. Se comprueba también la semántica `BLANK` de DAX, sin convertirla silenciosamente en cero.

## Presentación revisada

- Cuatro páginas de 1280 × 850 con una jerarquía común de cabecera, indicadores, gráficos y notas.
- Resumen con 4 891 clientes retenidos y tres filtros identificados: estado, edad y contrato.
- Títulos de gráficos ampliados y tooltips de tasas con clientes y bajas como denominador y numerador.
- Eliminación del límite de 20 categorías: se conservan los 51 estados y territorios y los 21 motivos.
- Notas sobre instantánea, datos ficticios, tamaños de segmentos y límites de causalidad.

La plantilla revisada se compiló y se volvió a extraer con pbi-tools. La comprobación estructural se registra en [`output/validacion_plantilla.json`](../output/validacion_plantilla.json). Compara el modelo, las páginas y los visuales recuperados con la fuente, comprueba campos existentes y detecta objetos fuera del lienzo o superpuestos. No simula el renderizado de Power BI.

## Límite de esta revisión

La captura y el árbol de accesibilidad de la ventana de Power BI no respondieron. Por ello no doy por comprobados los clics sobre los filtros, los tooltips ni la legibilidad final de las cuatro páginas. Tampoco presento una imagen reconstruida como captura del informe real. El modelo está validado; la aceptación visual e interactiva sigue pendiente.

Para cerrar esa revisión: abrir la plantilla, comprobar las cuatro páginas, seleccionar contrato mensual (3 411 clientes, 1 579 bajas, 46,29 %), combinar un estado y edad, quitar las selecciones y recuperar 6 687 / 1 796 / 26,86 %. Revisar que los tooltips muestran tamaños de segmento y que los gráficos permiten consultar todas las categorías sin cortar títulos o etiquetas.

## Repetir las pruebas

Con el CSV obtenido según [`data/README.md`](../data/README.md):

```powershell
python scripts/analizar.py
python scripts/preparar_pruebas_motor.py
```

Con la plantilla cargada en Power BI Desktop, indicar el puerto de su instancia local y la carpeta de bibliotecas TOM/ADOMD de una instalación compatible de pbi-tools. Son rutas locales, no credenciales:

```powershell
./scripts/validar_motor.ps1 -Port PUERTO_LOCAL -DependencyPath 'RUTA/pbi-tools/deps'
```

Para la comprobación del binario, extraerlo primero y pasar la carpeta resultante:

```powershell
pbi-tools extract entregables/Databel_abandono.pbit -extractFolder trabajo/revision_final_extraida -modelSerialization Raw
python scripts/validar_plantilla.py trabajo/revision_final_extraida
```

Las pruebas no modifican el modelo cargado. El avance previo al 100 % del caso en DataCamp no es una aprobación nueva de esta adaptación. La publicación en GitHub y el portafolio tampoco implica publicación en Power BI Service.
