"""decathlon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from deals.views import ProductListJson, product_datatables, price_chart_json

urlpatterns = [
    path('admin/', admin.site.urls),

    path("products_dt_json/", ProductListJson.as_view(), name="products_dt_json"),

    path("products/<str:country>/", product_datatables, name="products_dt"),

    path("price_history_json/<str:prod_id>/", price_chart_json, name="price_history_json"),

    path("price_history/<str:prod_id>/", TemplateView.as_view(template_name='price_history.html'), name="price_history"),
]
