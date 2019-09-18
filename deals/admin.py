from django.contrib import admin
from deals.models import Product, CountryWebsite, EmailRecipient, Price


class ProductAdmin(admin.ModelAdmin):
    list_display = ('prod_id', 'model_id', 'name', 'price_original', 'price_discounted', 'discount_percentage', 'url', 'country', 'include_in_report')
    list_filter = ('country', 'include_in_report')
    
    def price_original(self, obj):
        return obj.latest_price.price_original
        
    def price_discounted(self, obj):
        return obj.latest_price.price_original
        
    def discount_percentage(self, obj):
        return obj.latest_price.price_original


class CountryWebsiteAdmin(admin.ModelAdmin):
    list_display = ('country', 'base_url', 'deals_url')
    
    
class EmailRecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    
    
class PriceAdmin(admin.ModelAdmin):
    model = Price
    list_display = ('product_id', 'price_original', 'price_discounted', 'discount_percentage', 'updated_at')
    
    def prod_id(self, obj):
        return obj.product.prod_id
    
    def prod_name(self, obj):
        return obj.product.name
    
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(CountryWebsite, CountryWebsiteAdmin)
admin.site.register(EmailRecipient, EmailRecipientAdmin)
