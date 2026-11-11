"""Comprueba el PBIT reextraído contra su fuente; no reemplaza la revisión visual."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'powerbi/Databel'
EXTRACTED = Path(sys.argv[1]).resolve()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pages(root):
    result = {}
    for path in (root / 'Report/sections').glob('*/section.json'):
        page = read(path)
        visuals = {}
        for config_path in path.parent.glob('visualContainers/*/config.json'):
            config = read(config_path)
            files = {p.name: read(p) for p in config_path.parent.glob('*.json')}
            visuals[config['name']] = files
        result[page['name']] = (page, visuals)
    return result

source_model = read(SOURCE / 'Model/database.json')
extracted_model = read(EXTRACTED / 'Model/database.json')
assert source_model == extracted_model, 'El modelo reextraído difiere de la fuente'
source_pages, actual_pages = pages(SOURCE), pages(EXTRACTED)
assert source_pages.keys() == actual_pages.keys(), 'Páginas distintas'
columns = {t['name']: {c['name'] for c in t['columns']} for t in source_model['model']['tables']}
measures = {t['name']: {m['name'] for m in t['measures']} for t in source_model['model']['tables']}
counts = {}
for page_id, (page, visuals) in source_pages.items():
    actual_page, actual_visuals = actual_pages[page_id]
    assert page == actual_page, f"Página modificada: {page['displayName']}"
    assert visuals.keys() == actual_visuals.keys(), 'Visuales distintos'
    positions = []
    for visual_id, files in visuals.items():
        assert files == actual_visuals[visual_id], f'Visual modificado en el binario: {visual_id}'
        config = files['config.json']['singleVisual']
        pos = files['visualContainer.json']
        x, y, w, h = (pos[k] for k in ('x', 'y', 'width', 'height'))
        assert x >= 0 and y >= 0 and w > 0 and h > 0
        assert x+w <= page['width'] and y+h <= page['height'], 'Objeto fuera del lienzo'
        for px, py, pw, ph in positions:
            assert min(x+w, px+pw) <= max(x, px) or min(y+h, py+ph) <= max(y, py), 'Objetos superpuestos'
        positions.append((x, y, w, h))
        query = config.get('prototypeQuery')
        if query:
            tables = {s['Name']: s['Entity'] for s in query['From']}
            names = {s['Name'] for s in query['Select']}
            for select in query['Select']:
                kind = 'Measure' if 'Measure' in select else 'Column'
                expr = select[kind]
                table = tables[expr['Expression']['SourceRef']['Source']]
                assert expr['Property'] in (measures if kind == 'Measure' else columns)[table]
            for refs in config['projections'].values():
                assert all(ref['queryRef'] in names for ref in refs), 'Referencia sin consulta'
    counts[page['displayName']] = len(visuals)

result = {
    'status': 'OK',
    'pbit_sha256': digest(ROOT / 'entregables/Databel_abandono.pbit'),
    'model_definition_sha256': hashlib.sha256((SOURCE / 'Model/database.json').read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest(),
    'hash_normalization': 'UTF-8 sin BOM, saltos LF',
    'model_and_report_match_reextraction': True,
    'pages': counts,
    'objects_within_canvas': True,
    'object_overlaps': 0,
    'field_references_valid': True,
    'scope': 'Comprobación estructural. No demuestra renderizado, legibilidad ni interacción con clics.'
}
(ROOT / 'output/validacion_plantilla.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=True))
