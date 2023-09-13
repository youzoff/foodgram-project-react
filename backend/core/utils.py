from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.db import transaction
from django.http import FileResponse
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.paragraph import Paragraph

from recipes.models import Ingredient, Tag


def get_shopping_cart_pdf(data: list):
    styles = getSampleStyleSheet()
    styles['Heading1'].fontName = 'DejaVuSansMono'
    styles['Heading2'].fontName = 'DejaVuSansMono'
    styles['Normal'].fontName = 'DejaVuSansMono'

    registerFont(
        TTFont(
            'DejaVuSansMono',
            (
                f'{settings.BASE_DIR}{settings.STATIC_URL}'
                f'/fonts/DejaVuSansMono.ttf'
            ),
            'UTF-8',
        )
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        pagesize=A4,
        title='Список покупок',
        creator='youzoff',
    )

    story = []

    width, _ = portrait(A4)
    drawing = Drawing(width - 20, 1)
    drawing.add(Line(0, 0, width - 60, 0))
    story.append(drawing)

    story.append(
        Paragraph(
            'Сформирован: ' + datetime.today().strftime('%d/%m/%Y %H:%M'),
            styles['Normal']
        )
    )
    story.append(Paragraph('<br />\nСписок покупок:', styles['Heading1']))

    table = Table(data, colWidths=[12.5 * cm, 2.5 * cm, 3 * cm])

    table.setStyle(
        TableStyle(
            [
                ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
                ('SIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (1, 0), (1, -1), 'CENTRE'),
                ('ALIGN', (2, 0), (2, -1), 'CENTRE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('FONT', (0, 0), (-1, -1), 'DejaVuSansMono'),
            ]
        )
    )
    story.append(table)
    story.append(Paragraph('<br />\n <br />\n'))

    drawing2 = Drawing(width - 20, 1)
    drawing2.add(Line(0, 0, width - 60, 0))
    story.append(drawing2)

    story.append(
        Paragraph(
            '<br />\n Продуктовый помощник @FoodGram',
            styles['Heading2'],
        )
    )

    doc.build(story)
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shopping_cart.pdf'
    )


@transaction.atomic
def load_ingredients_data(ingredient_data):
    for row in ingredient_data:
        ingredient_name = row['name']
        measurement_unit = row['measurement_unit']
        ingredient, _ = Ingredient.objects.get_or_create(
            name=ingredient_name, measurement_unit=measurement_unit
        )


@transaction.atomic
def load_tags_data(tags_data):
    for row in tags_data:
        tag_name = row['name']
        tag_color = row['color']
        tag_slug = row['slug']
        tag, _ = Tag.objects.get_or_create(
            name=tag_name, color=tag_color, slug=tag_slug
        )
