# decadeals

A Django app allowing to fetch discounted products from Decathlon.pl and Decathlon.de.  
Products are stored in the databse together with their price history.  

Product list can be viewed in a DataTables-based table, price history is presented using Chart.js.  
Product list URL: http://server_url/products/[country], e.g. http://server_url/products/PL  
Price history charts are accesible from the product list.  

There are two Django commands that can be executed using "python manage.py command":
* fetch_products [country] [limit] - updates the product list, e.g. "fetch_products PL 2000" would fetch products from the Polish website up to 2000 products in a single run.
* generate_report [--send-email] - prepares a report of changed/new products since the last update and sends it to e-mail specified as EmailRecipient objects in Django admin panel.

For the script to be able to fetch products from a specific website, a set of XPaths pointing to price/product name/etc. fields in the webpage HTML has to be defined as a CountryWebsite object.  
Values for .pl and .de can be loaded from deals_website_settings.json file.  

This project is not anyhow related with Decathlon, it is just an example of a Django app.  

Live demo:  
http://ms93.ml:7000/products/PL/  
http://ms93.ml:7000/products/DE/  
