from django.core.management.base import BaseCommand, CommandError
from deals.utils import generate_report


class Command(BaseCommand):
    help = 'Generates a product changes report and optionally sends it by email'
    
    def add_arguments(self, parser):
        parser.add_argument('country', type=str, help='Two-letter country code [de, pl]')
        parser.add_argument('--send-email', dest='send_email', action='store_true', help='Send the report by email')
        parser.set_defaults(send_email=False)

    def handle(self, *args, **options):
        print(options)
        generate_report(options['country'], options['send_email'])
