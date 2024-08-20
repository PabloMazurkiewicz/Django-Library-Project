# library_app/management/commands/load_data_from_zip.py

from django.core.management.base import BaseCommand
from library_app.utils import load_data_from_zip  # Assuming the function is in utils.py

class Command(BaseCommand):
    help = 'Load books and authors from a zip file without unzipping'

    def add_arguments(self, parser):
        parser.add_argument('zip_path', type=str, help='The path to the zip file')

    def handle(self, *args, **kwargs):
        zip_path = kwargs['zip_path']
        load_data_from_zip(zip_path)
        self.stdout.write(self.style.SUCCESS('Successfully loaded books and authors from the zip file'))
