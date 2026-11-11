# Reconstruir la plantilla

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
