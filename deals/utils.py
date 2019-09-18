from deals.models import Product, Price, CountryWebsite, EmailRecipient
from django.core.mail import send_mail
import requests
from lxml import etree
from datetime import datetime


def fetch_products(country, limit):
    """Fetches a list of products for a selected country
    Arguments:
        country - country code corresponding to a CountryWebsite.country
        limit - number of maximum products to be fetched
    """
    # make sure country is uppercase
    country = country.upper()
    # get country-specific settings
    country_settings = CountryWebsite.objects.get(country=country)
    # calculate page count
    max_pages = int(limit/country_settings.per_page)
    # loop over pages
    for page_no in range(0, max_pages):
        print('Page:', page_no+1, 'of', max_pages)
        # prepare correct page numbering
        if country == 'PL':
            page_no_url = page_no + 1  # PL page numbering starts from 1
        elif country == 'DE':
            page_no_url = page_no * country_settings.per_page  # DE page numbering is related to article count
        else:
            page_no_url = page_no
        # create url - replace {{page_no}} with page number and {{per_page}} with page size
        url = country_settings.deals_url\
            .replace('{{page_no}}', str(page_no_url)).replace('{{per_page}}', str(country_settings.per_page))
        print(url)
        # get data and process html
        r = requests.get(url)
        tree = etree.HTML(r.text)
        # loop over products
        try:
            products = tree.xpath(country_settings.product_xpath)
            # some pages (eg DE) return a page with no <article> objects -> end loop when count is 0
            if len(products) == 0:
                print('No more products')
                break
            print('Products:', len(products))
            for product in products:
                try:
                    prod_id = country + product.xpath(country_settings.prod_id_xpath)[0].strip()
                    prod_model_id = int(product.xpath(country_settings.model_id_xpath)[0].strip())
                    prod_name = product.xpath(country_settings.name_xpath)[0].strip()
                    prod_category = product.xpath(country_settings.category_xpath)[0].strip()
                    prod_url = product.xpath(country_settings.url_xpath)[0].strip()
                    # strip prices of currency signs and separators, set dot as decimal separator
                    prod_price_old = ''.join(product.xpath(country_settings.price_original_xpath)).strip() \
                        .replace(country_settings.currency_symbol, '') \
                        .replace(country_settings.thousand_separator, '') \
                        .replace(country_settings.decimal_separator, '.')
                    prod_price_new = ''.join(product.xpath(country_settings.price_discounted_xpath)).strip() \
                        .replace(country_settings.currency_symbol, '') \
                        .replace(country_settings.thousand_separator, '') \
                        .replace(country_settings.decimal_separator, '.')
                    # convert prices from text to numbers
                    prod_price_old = float(prod_price_old)
                    prod_price_new = float(prod_price_new)
                    # create price object
                    price = Price(product_id=prod_id,
                                  price_original=prod_price_old,
                                  price_discounted=prod_price_new)
                    price.save()
                    # add product to database
                    prod = Product(prod_id=prod_id, model_id=prod_model_id,
                                   name=prod_name, category=prod_category,
                                   latest_price=price,
                                   url=prod_url,
                                   country=country)
                    prod.save_and_check_price()
                except (KeyError, IndexError, AttributeError, ValueError):
                    continue
        # some pages (eg PL) return empty page when no products -> end loop on AttributeError
        except AttributeError:
            print('No more products')
            break


def generate_report(country, send_email):
    """Generates an update report (based on Product.status_after_update values)
    and sends it as e-mail to e-mails stored as EmailRecipient objects if send_email=True
    or prints the report out if send_email=False
    Arguments:
        send_email - whether to send the report by e-mail (True/False)
        country - country code corresponding to a CountryWebsite.country
    """
    report_from_email = 'aws@ms93.pl'
    # get products to report
    products_to_report_new = Product.objects.filter(include_in_report=True,
                                                    status_after_update='new',
                                                    country__iexact=country)
    products_to_report_changed = Product.objects.filter(include_in_report=True,
                                                        status_after_update='changed',
                                                        country__iexact=country)
    # assemble report body
    report_body = ''
    for product in products_to_report_new:
        report_body += 'NEW\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'\
            .format(product.prod_id, product.model_id, product.latest_price.price_original,
                    product.latest_price.price_discounted, product.latest_price.discount_percentage,
                    product.name, product.category, product.full_url)
    for product in products_to_report_changed:
        report_body += 'CHANGE\t{}\t{}\t{}\t{}\t{}->{}\t{}\t{}\t{}\n'\
            .format(product.prod_id, product.model_id,
                    product.latest_price.price_original,
                    product.prices[1].price_discounted, product.latest_price.price_discounted,
                    product.latest_price.discount_percentage,
                    product.name, product.category, product.full_url)
    # send email
    if len(report_body) > 1:
        if send_email is True:
            recipient_list = [x.email for x in EmailRecipient.objects.filter(active=True, country__country=country)]
            print('Sending e-mails to:', ', '.join(recipient_list))
            send_mail(
                subject='Decathlon report for {} ({})'.format(country, datetime.now().strftime('%Y-%m-%d %H:%M')),
                message=report_body,
                from_email=report_from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        else:
            print(report_body)
    else:
        print('Report empty.')
    # mark as reported
    products_to_report_new.update(include_in_report=False)
    products_to_report_changed.update(include_in_report=False)
