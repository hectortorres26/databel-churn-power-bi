"""Monta un PDF con vistas reales de Power BI, sin redibujar sus gráficos.

Entrada privada: trabajo/render_presentacion/*.png, producida por el CLI oficial.
El recorte del lienzo se hace en la composición PDF; se conserva cada imagen fuente.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['Resumen', 'Segmentos', 'Contratos y planes', 'Motivos y calidad']
TARGET = ROOT / 'docs/Presentacion_dashboard_Databel.pdf'
# Coordenadas verificadas sobre las vistas nativas de esta sesión.
CROP_X, CROP_Y, CROP_W, CROP_H = 0, 482, 1048, 695
PAGE_W, PAGE_H = 1100, 765
pdf = canvas.Canvas(str(TARGET), pagesize=(PAGE_W, PAGE_H))
pdf.setTitle('Databel | Dashboard para presentación')
pdf.setAuthor('Hector Americo Torres Huamani')
for number, name in enumerate(PAGES, 1):
    img = ImageReader(str(ROOT / 'trabajo/render_presentacion' / (name + '.png')))
    width, height = img.getSize()
    assert (width, height) == (1114, 1658), 'Revisar el recorte si cambia el tamaño de la vista'
    x, y = 26, 48
    pdf.saveState()
    clip = pdf.beginPath(); clip.rect(x, y, CROP_W, CROP_H)
    pdf.clipPath(clip, stroke=0)
    pdf.drawImage(img, x-CROP_X, y-(height-CROP_Y-CROP_H), width=width, height=height)
    pdf.restoreState()
    pdf.setFillColorRGB(.2, .3, .36); pdf.setFont('Helvetica', 10)
    pdf.drawString(26, 29, 'Hector Americo Torres Huamani | Caso educativo basado en DataCamp')
    pdf.drawRightString(1074, 29, f'{number} / 4')
    pdf.setFont('Helvetica', 8)
    pdf.drawString(26, 14, 'Vista real de Power BI. PDF estático: filtros y desplazamiento están disponibles en el proyecto PBIP.')
    pdf.showPage()
pdf.save()
print(TARGET)
