import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from core.utils import load_ingredients_data


class Command(BaseCommand):
    help = _('Loading data from CSV')

    def handle(self, *args, **kwargs):
        with open(settings.CSV_PATH, 'r') as csv_file:
            data = csv.DictReader(csv_file, fieldnames=('name', 'unit'))
            load_ingredients_data(data)

        self.stdout.write(
            self.style.SUCCESS(_('Data download completed'))
        )
