# Validación del dashboard Databel

Revisión final del 11 de noviembre de 2026 (hora de Lima), después del rediseño visual. Separé las pruebas de datos, modelo y presentación para que el estado del proyecto sea verificable.

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
| Catorce combinaciones de dimensión y medida de los gráficos | Todas coinciden, categoría por categoría |
| Mismo modelo en fuente y sesión cargada | Correcto |

Los filtros incluyen los tres contratos, dos grupos de edad, California, California con contrato mensual, actividad internacional cruzada con plan, clientes retenidos, una selección sin registros y el total restablecido. Se comprueba también la semántica `BLANK` de DAX, sin convertirla silenciosamente en cero.

## Presentación revisada

- Cuatro páginas de 1440 × 900 y 46 objetos, con una jerarquía común de cabecera, indicadores, gráficos y notas.
- Resumen con 4 891 clientes retenidos y tres filtros identificados: estado, edad y contrato.
- Títulos de gráficos ampliados y tooltips de tasas con clientes y bajas como denominador y numerador.
- Eliminación del límite de 20 categorías: se conservan los 51 estados y territorios y los 21 motivos.
- Notas sobre instantánea, datos ficticios, tamaños de segmentos y límites de causalidad.

La plantilla revisada se compiló y se volvió a extraer con pbi-tools. La comprobación estructural se registra en [`output/validacion_plantilla.json`](../output/validacion_plantilla.json). Compara el modelo, las páginas y los visuales recuperados con la fuente, comprueba campos existentes y detecta objetos fuera del lienzo o superpuestos. No simula el renderizado de Power BI.

## Validación nativa y alternativa de acceso

La automatización general de captura y accesibilidad no consiguió leer la ventana. Resolví el bloqueo mediante el [CLI oficial de autoría de Power BI](https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-skill-overview), versión 0.5.0. Convertí las definiciones propias a PBIP/PBIR y conservé el mismo modelo. El CLI se conectó a Desktop y obtuvo las vistas reales de sus cuatro páginas. No se sustituyeron por una recreación HTML ni por gráficos dibujados fuera de Power BI.

La validación de esquemas terminó con **0 errores y 0 advertencias**. Revisé las cuatro vistas y corregí títulos recortados, encabezados de filtros y columnas de valores que no aparecían en las tablas. Las tablas de estados y motivos conservan desplazamiento: la presentación estática muestra la porción inicial, mientras el proyecto nativo y los CSV permiten consultar el detalle completo.

Al guardar, Desktop convirtió el modelo BIM a TMDL. Comprobé mediante el lector TOM que las nueve medidas, los tipos de columnas, Power Query y el parámetro de fuente coinciden con el modelo validado; el resultado está en `output/validacion_tmdl.json`. El guardado también retiró dos referencias de esquema y utilizó un esquema de contenedores aún no accesible al validador. Restauré las referencias públicas compatibles y repetí la validación y el renderizado sin cambiar los visuales ni sus datos.

Para probar los controles sin automatizar el ratón, guardé selecciones en la propiedad nativa `general.filter` de los segmentadores, recargué el informe en Desktop y contrasté los resultados visibles con pandas y DAX. Son filtros aplicados por el informe real, no solo consultas aisladas.

| Selección cargada | Resultado visible confirmado |
|---|---|
| Contrato mensual | 3 411 clientes; 1 579 bajas; 46,29 %; 1 832 retenidos |
| California y contrato mensual | 33 clientes; 26 bajas; 78,79 %; 7 retenidos |
| Edad de 65 o más | 1 256 clientes; 483 bajas; 38,46 %; 773 retenidos |
| Actividad internacional = Yes | Sin plan: 40,34 %; con plan: 7,59 % |
| Todas las selecciones eliminadas | 6 687 clientes; 1 796 bajas; 26,86 %; 4 891 retenidos |

El proyecto se entrega en el estado sin selecciones. No afirmo haber probado clics de ratón, hover de tooltips ni cada combinación posible. Sus campos y relaciones se verificaron estructuralmente; las pruebas nativas cubren las selecciones indicadas. La interacción entre barras está configurada como filtrado, pero no se ensayó mediante clics.

La [presentación PDF](Presentacion_dashboard_Databel.pdf) reúne las vistas reales y solo recorta el espacio gris exterior del host. Es una composición para exposición, no una exportación PDF realizada desde el menú de Power BI. El [registro nativo](../output/validacion_nativa.json) documenta versiones, alcance y huellas de los archivos.

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

Para repetir las comprobaciones del informe nativo, instala el CLI en una carpeta de herramientas y usa una versión de Desktop compatible. La instalación utilizada fue `npm install --prefix trabajo/herramientas @microsoft/powerbi-report-authoring-cli@0.5.0`. Consulta también [Reconstrucción](reconstruccion.md).

```powershell
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js validate powerbi/DatabelPresentacion/Databel.Report
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js preview powerbi/DatabelPresentacion/Databel.Report --host desktop --status
python scripts/seleccionar_escenario.py mensual
# Solo recargar cuando no haya cambios manuales sin guardar.
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js preview powerbi/DatabelPresentacion/Databel.Report --host desktop --reload
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js preview powerbi/DatabelPresentacion/Databel.Report --host desktop --screenshot trabajo/mensual.png --page Resumen
python scripts/seleccionar_escenario.py base
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js preview powerbi/DatabelPresentacion/Databel.Report --host desktop --reload
```

Los otros escenarios son `ca_mensual`, `mayores` e `internacional`; este último se revisa en «Contratos y planes». Al terminar siempre se restaura `base`. El script modifica únicamente las selecciones guardadas del informe, por lo que conviene trabajar en una copia si se han personalizado los segmentadores.
