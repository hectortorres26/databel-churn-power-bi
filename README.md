# Databel: diagnóstico del abandono de clientes

**Hector Americo Torres Huamani · Power BI, Power Query y DAX**

Analicé una instantánea de **6 687 clientes** de Databel, una empresa ficticia de telecomunicaciones, para identificar cómo se distribuye el abandono entre contratos, perfiles y planes. Encontré **1 796 bajas**, equivalentes al **26,86 %** de los clientes.

Preparé una adaptación en Power BI con cuatro páginas y nueve medidas DAX, y contrasté los indicadores con Python. El informe organiza el diagnóstico para distinguir tasas, volumen de clientes y motivos declarados.

> Basado en el caso educativo [Case Study: Analyzing Customer Churn in Power BI](https://app.datacamp.com/learn/courses/case-study-analyzing-customer-churn-in-power-bi) de DataCamp. El dataset y el esquema inicial proceden de sus materiales. Las páginas de esta adaptación, las medidas en español, el tratamiento explícito de motivos ausentes y la auditoría independiente están documentados aquí.

## Explorar

- [Plantilla de Power BI](entregables/Databel_abandono.pbit).
- [Notebook de validación independiente](Validacion_Databel.ipynb).
- [Reporte y guía de medidas](docs/Reporte_y_guia_Databel.pdf).
- [Medidas DAX](docs/medidas.dax) y [Power Query](docs/transformaciones.pq).
- [Obtención y procedencia de datos](data/README.md).
- [Resultados calculados](output/metricas.json).

## Resultados principales

| Indicador o segmento | Resultado |
|---|---:|
| Clientes | 6 687 |
| Bajas | 1 796 |
| Tasa global | 26,86 % |
| Contrato mensual | 1 579 / 3 411: 46,29 % |
| Contrato de un año | 167 / 1 479: 11,29 % |
| Contrato de dos años | 50 / 1 797: 2,78 % |
| Bajas asociadas a competencia | 805: 44,82 % de todas las bajas |
| Bajas sin motivo registrado | 27: 1,50 % de todas las bajas |

La distribución de motivos incluye los casos sin información: el denominador es **1 796**, no solo las **1 769** bajas con un motivo conocido. No encontré filas duplicadas ni identificadores de cliente repetidos.

Los usuarios con actividad internacional y sin plan internacional presentan un 40,34 % de abandono; quienes tienen actividad y plan, un 7,59 %. La comparación sugiere investigar la adecuación de los planes, pero no demuestra que contratar uno reduzca el abandono.

## Páginas del informe

1. **Resumen:** clientes, bajas, tasa y motivos ausentes; comparación por contrato y filtros de estado y edad.
2. **Segmentos:** tasas y volumen por edad, comparación geográfica y pertenencia a grupos.
3. **Contratos y planes:** pagos, planes internacionales y de datos, atención al cliente y filtro de actividad internacional.
4. **Motivos y calidad:** desglose de motivos y controles de integridad.

El reporte usa barras para la comparación de estados. Los rankings visuales limitan categorías para conservar legibilidad; las tablas CSV contienen el detalle completo.

## Cómo abrir y actualizar

Abre `entregables/Databel_abandono.pbit` en Power BI Desktop. El parámetro `FuenteCSV` admite la URL propuesta del CSV público original o una ruta absoluta al archivo descargado. La plantilla no incluye datos cargados. Una conexión web pública puede requerir seleccionar acceso anónimo en Power BI.

Para repetir la auditoría independiente, usa Python 3.11, instala `requirements.txt`, coloca el CSV original como explica [Datos](data/README.md) y ejecuta:

```powershell
python scripts/analizar.py
```

El notebook se ejecuta desde la raíz del repositorio. El análisis exporta únicamente agregaciones; no publica teléfonos ni filas individuales. Power Query elimina el teléfono del modelo y oculta el identificador de cliente del panel de campos.

Las definiciones de `powerbi/Databel` están en formato **PbixProj de pbi-tools**, no PBIP nativo. La reconstrucción de la plantilla requiere una versión compatible de pbi-tools y Power BI Desktop. Se conserva la plantilla compilada para abrirla directamente. Consulta las [instrucciones de reconstrucción](docs/reconstruccion.md), incluida la procedencia del esquema inicial y la limitación de compatibilidad encontrada.

## Primera prueba y mejora

La primera exploración permitió calcular la tasa global y comparar contratos. La revisión detectó que los nulos de motivos combinaban clientes retenidos y 27 bajas sin motivo. La adaptación separa «No aplica» de «Sin motivo informado», mantiene el total de bajas y muestra tamaños de segmentos junto con sus tasas.

También distinguí la antigüedad de la cuenta de una fecha de observación. El dataset es una instantánea: no construí una tendencia mensual a partir de la antigüedad ni añadí predicciones que el ejercicio no requiere.

## Validación y estado

- Auditoría con pandas y recuento independiente con la biblioteca estándar: correctos.
- Los totales de los segmentos y motivos se reconcilian con 6 687 clientes y 1 796 bajas.
- Plantilla compilada correctamente; contiene cuatro páginas y nueve medidas.
- Consultas DAX ejecutadas correctamente en el modelo inicial de DataCamp, mediante su laboratorio de Power BI en Edge: clientes, bajas, tasa, duplicados, motivos vacíos y los tres tipos de contrato coinciden con la auditoría. Consulta la [validación del motor](docs/validacion_edge.md).
- **Pendiente:** cargar la plantilla propia de cuatro páginas y verificar sus transformaciones, visuales e interacciones. El laboratorio utiliza archivos de una máquina remota y no se observó un control para cargar la plantilla local. Validar consultas sobre el modelo inicial no equivale a validar ese archivo PBIT.
- DataCamp mostraba los tres capítulos al 100 % **antes** de esta adaptación. No presento ese progreso previo como aprobación de este nuevo archivo por el corrector.

## Conclusiones y límites

Priorizaría la revisión de contratos mensuales y la adecuación de planes internacionales. La competencia es el motivo declarado más frecuente. Estas son hipótesis de trabajo basadas en asociaciones de una muestra ficticia; no se cuantifican efectos causales, ingresos recuperables ni resultados de producción.

Los motivos solo se conocen después del abandono. No deben utilizarse como predictores de una baja futura. Los estados o segmentos pequeños requieren cautela y las comparaciones no ajustan simultáneamente por todas las variables.
