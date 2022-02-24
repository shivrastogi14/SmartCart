# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import importlib
import time

from config import parameters as pm
# from domain_parser import bestbuy as bb


# SETUP GLOBAL VARIABLES
driver_location = r'F:\Chromium'
os.environ['PATH'] += f";{driver_location};"
# os.environ['PATH'] += r":/Users/shivrastogi/Desktop/Python/:"


def get_product():
    try:
        site = input('Enter the URL for product:= ').strip()
        section = site.split('skuId=')
        sku_id = section[1]
        parts = section[0].split('/')
        desc = parts[4]
        www = parts[2].split('.')[0].lower()
        if www == 'www':
            tld1 = parts[2].split('.')[1]
        else:
            tld1 = parts[2].split('.')[0]
        return sku_id, tld1, desc, site
    except (IndexError, ValueError, TypeError) as e:
        print('URL format should be https://<www.sitename.com>/...?skuid=9999999')
        print(e)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Lets get started')
    skuid, tld, descr, url = get_product()
    print(skuid, tld, descr)
    filename = os.path.join(driver_location, tld, 'parameters.ini')
    if not os.path.exists(filename):
        pm.first_time_param(filename, tld)
    else:
        # TODO: based upon text messaging selection by user
        #  change "all" to "None" for NOT reading twilio data
        from config import parameters as pm
        param_obj = pm.config_read(filename, tld, 'all')
        print('Found config file, reading parameters...')
        m_parse = importlib.import_module('domain_parser' + '.' + tld)
        bb = m_parse.BestBuy(url, **param_obj).start(600)

