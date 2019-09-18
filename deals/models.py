from django.db import models
from django.utils import timezone


class Price(models.Model):
    product_id = models.CharField(max_length=20)
    price_original = models.DecimalField(max_digits=8, decimal_places=2)
    price_discounted = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percentage = models.IntegerField()
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # save and calculate discount percentage
        self.discount_percentage = int((1 - self.price_discounted / self.price_original) * 100)
        super(Price, self).save(*args, **kwargs)


class Product(models.Model):
    prod_id = models.CharField(max_length=20, primary_key=True, db_index=True)
    model_id = models.IntegerField()
    name = models.TextField()
    category = models.TextField()
    latest_price = models.ForeignKey(Price, on_delete=models.CASCADE)
    url = models.TextField()
    country = models.CharField(max_length=5)
    status_after_update = models.CharField(max_length=20, blank=True)
    include_in_report = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def save_and_check_price(self, *args, **kwargs):
        # check if there is a previous price
        try:
            previous_price = self.prices[1]
            # price change check
            if float(previous_price.price_discounted) != float(self.latest_price.price_discounted):
                self.include_in_report = True
                self.status_after_update = 'changed'
                print('CHANGE\t', self.prod_id, self.model_id, self.name, self.latest_price.price_original,
                      previous_price.price_discounted, '->', self.latest_price.price_discounted,
                      self.latest_price.discount_percentage, self.category, self.url)
            # price has not changed
            else:
                self.include_in_report = False
                self.status_after_update = 'unchanged'
        # no price found -> new entry
        except IndexError:
            self.include_in_report = True
            self.status_after_update = 'new'
            print('NEW\t', self.prod_id, self.model_id, self.name, self.latest_price.price_original,
                  self.latest_price.price_discounted, self.latest_price.discount_percentage, self.category, self.url)
        # save product
        super(Product, self).save(*args, **kwargs)

    @property
    def full_url(self):
        # full product url containing also the website domain
        base_url = CountryWebsite.objects.get(country=self.country).base_url
        return base_url + self.url
    
    @property
    def prices(self):
        # returns product historical prices
        try:
            return Price.objects.filter(product_id=self.prod_id).order_by('-updated_at')
        except AttributeError:
            return 0
        except IndexError:
            return None


class CountryWebsite(models.Model):
    country = models.CharField(max_length=5, primary_key=True, db_index=True)
    base_url = models.TextField()
    deals_url = models.TextField()
    product_xpath = models.TextField()
    per_page = models.IntegerField()
    prod_id_xpath = models.TextField()
    model_id_xpath = models.TextField()
    name_xpath = models.TextField()
    category_xpath = models.TextField()
    price_original_xpath = models.TextField()
    price_discounted_xpath = models.TextField()
    url_xpath = models.TextField()
    currency_symbol = models.CharField(max_length=20, blank=True)
    decimal_separator = models.CharField(max_length=20, blank=True)
    thousand_separator = models.CharField(max_length=20, blank=True)


class EmailRecipient(models.Model):
    name = models.CharField(max_length=100, primary_key=True, db_index=True)
    email = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    country = models.ForeignKey(CountryWebsite, on_delete=models.DO_NOTHING)
