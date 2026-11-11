"""Empaqueta el proyecto nativo y sus documentos, sin cachés ni filas originales."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'powerbi/DatabelPresentacion'
target=ROOT/'entregables/Databel_dashboard_redisenado.zip'
instructions='''DATABEL | Diagnóstico del abandono de clientes
Hector Americo Torres Huamani - Rediseño del 11 de noviembre de 2026

1. Extraer TODO el ZIP en una carpeta.
2. Abrir DatabelPresentacion/Databel.pbip con Power BI Desktop compatible con PBIP/PBIR.
   Conservar Databel.Report y Databel.SemanticModel junto al archivo PBIP.
3. Pulsar Actualizar para cargar el CSV original de DataCamp.
   Si solicita autenticación para la URL pública, seleccionar Anónimo.
   El parámetro FuenteCSV también admite una ruta local al CSV original.

Alternativa: abrir Databel_abandono.pbit y cargar los datos.
Para exponer sin Power BI: abrir Presentacion_dashboard_Databel.pdf.
El PDF es estático; filtros y desplazamiento funcionan en el informe nativo.

Totales esperados: 6 687 clientes, 1 796 bajas, 26,86 % de abandono.
Datos ficticios del caso educativo de DataCamp. Sin dimensión temporal.
El paquete no incorpora datos individuales ni caché del modelo.
Código, fuentes y documentación: https://github.com/hectortorres26/databel-churn-power-bi
'''
with ZipFile(target,'w',ZIP_DEFLATED) as archive:
    for path in sorted(project.rglob('*')):
        if path.is_file() and '.pbi' not in path.parts and path.suffix!='.abf':
            archive.write(path,'DatabelPresentacion/'+path.relative_to(project).as_posix())
    for rel in ['entregables/Databel_abandono.pbit','docs/Presentacion_dashboard_Databel.pdf','docs/Reporte_y_guia_Databel.pdf']:
        archive.write(ROOT/rel,Path(rel).name)
    archive.writestr('LEEME.txt',instructions.encode('utf-8'))
with ZipFile(target) as archive:
    assert archive.testzip() is None
    names=archive.namelist()
    for required in ['DatabelPresentacion/Databel.pbip','DatabelPresentacion/Databel.Report/definition.pbir','DatabelPresentacion/Databel.SemanticModel/definition.pbism']:
        assert required in names,required
    assert any(n in names for n in ['DatabelPresentacion/Databel.SemanticModel/model.bim','DatabelPresentacion/Databel.SemanticModel/definition/model.tmdl'])
    assert not any('/.pbi/' in name or name.endswith('.abf') for name in names)
print(f'ZIP verificado: {target} ({len(names)} archivos)')
