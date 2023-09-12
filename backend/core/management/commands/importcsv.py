import csv
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from core.utils import load_ingredients_data, load_tags_data


class Command(BaseCommand):
    help = _('Loading data from CSV')

    def handle(self, *args, **kwargs):
        files = {
            'ingredients': {
                'file_name': 'ingredients.csv',
                'fieldnames': ('name', 'measurement_unit'),
                'import_func': load_ingredients_data
            },
            'tags': {
                'file_name': 'tags.csv',
                'fieldnames': ('name', 'color', 'slug'),
                'import_func': load_tags_data
            }
        }
        for file in files.values():
            path = os.path.join(settings.CSV_PATH, file.get('file_name'))
            with open(path, 'r') as csv_file:
                data = csv.DictReader(
                    csv_file,
                    fieldnames=file.get('fieldnames')
                )
                file.get('import_func')(data)
                self.stdout.write(
                    self.style.SUCCESS(_(
                        f'{file.get("file_name")} download completed'
                    ))
                )

        self.stdout.write(
            self.style.SUCCESS(_('Data download completed'))
        )
