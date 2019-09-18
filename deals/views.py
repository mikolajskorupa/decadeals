from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.template import loader
from django_datatables_view.base_datatable_view import BaseDatatableView
from deals.models import Product


def product_datatables(request, country):
    """ return a datatables table of Products """
    template = loader.get_template('products_dt.html')
    context = {
        'country': country,
    }
    return HttpResponse(template.render(context, request))


class ProductListJson(BaseDatatableView):
    """ return Products in JSON form for datatables """
    model = Product

    columns = ['prod_id', 'model_id', 'name', 'latest_price.price_original', 'latest_price.price_discounted',
               'latest_price.discount_percentage', 'full_url', 'country', 'updated_at', 'price_history']

    max_display_length = 500

    def render_column(self, row, column):
        if column == 'full_url':
            return '<a href="' + row.full_url + '">' + row.full_url + '</a>'
        if column == 'price_history':
            return '<a href="../../price_history/' + row.prod_id + '" target="_blank">' + row.prod_id + '</a>'
        else:
            return super(ProductListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # filter by country
        country = self.request.GET.get('country', 'PL')
        qs = qs.filter(country=country)
        # use parameters passed in GET request to filter queryset
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


def price_chart_json(request, prod_id):
    """ return Prices of a Product in JSON for chart.js """
    prices = Product.objects.get(prod_id=prod_id).prices
    labels = []
    data = []
    for price in prices:
        labels.append(price.updated_at.strftime('%Y-%m-%d %H:%M'))
        data.append(price.price_discounted)
    output = {
        'labels': labels,
        'datasets': [
            {
                'data': data,
                'label': prod_id,
                'name': prod_id,
            }
        ]
    }
    return JsonResponse(output)
