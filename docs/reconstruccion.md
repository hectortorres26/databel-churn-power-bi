# Reconstruir el proyecto y la plantilla

## Proyecto nativo recomendado

`powerbi/DatabelPresentacion/Databel.pbip` abre el informe PBIR y el modelo `model.bim` asociados. Descarga el repositorio completo y actualiza la fuente en Desktop. El archivo PBIP por sí solo no contiene el informe.

El caché `.pbi/cache.abf` permite abrir localmente los datos ya cargados, pero está excluido de Git junto con los archivos ABF. Una descarga del repositorio requiere **Actualizar**. No hay credenciales ni filas individuales publicadas. Esta separación sigue la [estructura de proyectos de Microsoft](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).

Para regenerar el informe después de modificar `powerbi/Databel`, instala el CLI oficial y ejecuta `python scripts/crear_pbip.py`. El repositorio ya incluye su esqueleto y tema. Solo si partes de una carpeta nueva, crea primero el esqueleto:

```powershell
npm install --prefix trabajo/herramientas @microsoft/powerbi-report-authoring-cli@0.5.0
node trabajo/herramientas/node_modules/@microsoft/powerbi-report-authoring-cli/dist/cli.js scaffold powerbi/DatabelPresentacion --name Databel --model-path ../Databel.SemanticModel --page-name Resumen --offline
python scripts/crear_pbip.py
```

El generador reemplaza las páginas propias: conserva una copia si las personalizaste. `scripts/cache_modelo_local.ps1` es una utilidad opcional para guardar un caché privado desde un modelo ya cargado y validado; no se necesita para abrir y actualizar un proyecto descargado. Se validó con Desktop 2.159.1231.0 y CLI 0.5.0. Consulta el procedimiento de filtros y vistas en [Validación](validacion_dashboard.md).

## Alternativa PBIT

Para abrir el informe utiliza la plantilla de `entregables`. No hace falta reconstruirla. Para compilar las definiciones incluidas se necesita una combinación compatible de Power BI Desktop y pbi-tools:

```powershell
pbi-tools compile powerbi/Databel -outPath entregables/Databel_abandono.pbit -format PBIT -overwrite
```

`powerbi/Databel` es PbixProj de pbi-tools; no es un proyecto PBIP de Microsoft.

El generador `scripts/construir_informe.py` parte del esquema inicial de los materiales oficiales, que no se redistribuyen. Para repetir esa etapa:

1. Descarga los materiales desde la página del caso de DataCamp, indicada en `data/README.md`.
2. Extrae `Exercises/1_1_data_check_solution.pbix`. Este archivo es una referencia de DataCamp, no un informe propio.
3. Extrae su modelo en la carpeta privada de trabajo con el comando siguiente, sustituyendo la ruta al archivo descargado.

```powershell
pbi-tools extract 'RUTA/1_1_data_check_solution.pbix' -extractFolder trabajo/modelo_base -modelSerialization Raw
python scripts/construir_informe.py
```

Después compila las definiciones. El generador reemplaza medidas y páginas por la adaptación descrita en el README. Conserva una copia antes de regenerar si modificaste esas definiciones manualmente.

Durante la preparación se detectó una incompatibilidad entre pbi-tools 1.2.0 y la firma del empaquetador de Power BI 2.159. Se compiló con un adaptador local ya disponible. Ese binario no se distribuye y no se garantiza que el comando funcione con cualquier versión instalada. Abrir la plantilla compilada y revisar su carga sigue siendo una comprobación separada de la compilación.
