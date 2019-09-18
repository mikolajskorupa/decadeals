from django.core.management.base import BaseCommand, CommandError
from deals.utils import fetch_products

class Command(BaseCommand):
    help = 'Fetches discounted products from a website'
    
    def add_arguments(self, parser):
        parser.add_argument('country', type=str, help='Two-letter country code [DE, PL]')
        parser.add_argument('limit', type=int, help='Limit of articles')

    def handle(self, *args, **options):
        fetch_products(options['country'], options['limit'])