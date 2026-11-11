"""Monta un PDF con vistas reales de Power BI, sin redibujar sus gráficos.

Entrada privada: trabajo/render_redisenio_final/*.png, producida por el CLI oficial.
El recorte del lienzo se hace en la composición PDF; se conserva cada imagen fuente.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['Resumen', 'Segmentos', 'Contratos y planes', 'Motivos y calidad']
TARGET = ROOT / 'docs/Presentacion_dashboard_Databel.pdf'
# Coordenadas verificadas sobre las vistas nativas de esta sesión.
CROP_X, CROP_Y, CROP_W, CROP_H = 172, 0, 2624, 1640
DRAW_W, DRAW_H = 1440, 900
PAGE_W, PAGE_H = 1488, 972
pdf = canvas.Canvas(str(TARGET), pagesize=(PAGE_W, PAGE_H))
pdf.setTitle('Databel | Dashboard para presentación')
pdf.setAuthor('Hector Americo Torres Huamani')
for number, name in enumerate(PAGES, 1):
    img = ImageReader(str(ROOT / 'trabajo/render_redisenio_final' / (name + '.png')))
    width, height = img.getSize()
    assert (width, height) == (3034, 1640), 'Revisar el recorte si cambia el tamaño de la vista'
    x, y, scale = 24, 48, DRAW_W/CROP_W
    pdf.saveState()
    clip = pdf.beginPath(); clip.rect(x, y, DRAW_W, DRAW_H)
    pdf.clipPath(clip, stroke=0)
    pdf.drawImage(img, x-CROP_X*scale, y-(height-CROP_Y-CROP_H)*scale, width=width*scale, height=height*scale)
    pdf.restoreState()
    pdf.setFillColorRGB(.2, .3, .36); pdf.setFont('Helvetica', 10)
    pdf.drawString(24, 29, 'Databel | Rediseño visual | 11 de noviembre de 2026')
    pdf.drawRightString(PAGE_W-24, 29, f'{number} / 4')
    pdf.setFont('Helvetica', 8)
    pdf.drawString(24, 14, 'Vista real de Power BI. PDF estático: filtros y desplazamiento están disponibles en el proyecto PBIP.')
    pdf.showPage()
pdf.save()
print(TARGET)
