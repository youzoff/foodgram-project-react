import os
from io import BytesIO

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from recipes.models import Ingredient, Recipe, Tag


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(
            settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, '')
        )
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(
            settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, '')
        )
    else:
        path = None
    return path


def get_shopping_list_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), result,
        encoding='UTF-8',
        link_callback=fetch_pdf_resources,
    )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')


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
