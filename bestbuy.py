# TODO - add Logger
# TODO - add debug to output extra data
# TODO - parse product link passed to compare SKU (should always be same)
# TODO - create a secrets file for sensitive information
# TODO - stop computer from going to sleep
# TODO - Test workaround for signUp dialog box
# TODO - Some items are only limited to 3 per order and this is not handled in method add-to-cart


import os
import sys
import time
import datetime

from selenium import webdriver
# from selenium_stealth import stealth      # package does not exist on conda-forge
import selenium.common.exceptions as error
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

import configparser
# import config.py

# SETUP GLOBAL VARIABLES
driver_location = r'F:\Chromium\\'
os.environ['PATH'] += r";F:\Chromium/;"
# os.environ['PATH'] += r":/Users/shivrastogi/Desktop/Python/:"
# print(os.environ['PATH'])
tld = 'bestbuy'
credentials = os.path.join(driver_location, tld)
# set absolute path to config file
filename = os.path.join(credentials+'\\parameters')
print(filename)

site = 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3070-8gb-gddr6-pci' \
       '-express-4-0-graphics-card-dark-platinum-and-black/6429442.p?skuId=6429442'
# site = 'https://www.bestbuy.com/site/insignia-9-play-charge-usb-c-cable-for-playstation' \
#        '-5-white-black/6424521.p?skuId=6424521'


os.chdir(credentials)
config = configparser.ConfigParser()
config.read(filename)
t_ph = config['TWILIO']['t_ph']
f_ph = config['TWILIO']['f_ph']
account_sid = config['TWILIO']['account_sid']
auth_token = config['TWILIO']['auth_token']
f_name = config[tld]['first_name']
l_name = config[tld]['last_name']
add = config[tld]['address']
city = config[tld]['city']
state = config[tld]['state']
zip_code = config[tld]['zip_code']
ph = config[tld]['phone']
membership = config[tld]['member_number']
cc_number = config[tld]['credit_card']
my_email = config[tld]['email']
my_password = config[tld]['password']

print(t_ph, f_ph, f_name, l_name, add, city, state, zip_code, ph, membership, cc_number, account_sid,
      auth_token, my_email, my_password)


def load(my_site):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('user-data-dir=F:/Chromium/Chrome_Profile')
    # TODO - autodetect chrome version and update in user-agent string below
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # stealth(driver,
    #     languages=["en-US", "en"],
    #     vendor="Google Inc.",
    #     platform="Win32",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine",
    #     fix_hairline=True,
    #     )
    # chrome_options.add_argument('--headless')
    no_image = {'profile.managed_default_content_settings.images': 2}
    chrome_options.add_experimental_option('prefs', no_image)
    driver = webdriver.Chrome(options=chrome_options)  # opens browser
    driver.set_window_size(1200, 900)  # reduce browser size
    driver.get(my_site)
    # print(driver.get_cookies())  # print to LOG when debug is ON
    return driver


def online_deal(driver):
    # Just for checking if it is online only or best buy brand
    try:
        driver.find_element_by_class_name('badge-image')
        print('Online Only Deal')
    except error.NoSuchElementException:
        print('Also available in store')
        # TODO - update zip code to point to correct store


def survey_check(driver):
    # wait for survey alert/popup to load and switch to it
    # else add to cart will fail coz add-to-cart button is not clickable
    # selenium.common.exceptions.ElementClickInterceptedException
    try:
        WebDriverWait(driver, 5).until(expect.presence_of_element_located((By.ID, 'survey_invite_no')))
        click_no = driver.find_element_by_id('survey_invite_no')
        click_no.click()
    except (error.TimeoutException, error.NoSuchElementException):
        print('Survey element not found')


def login_check(driver):
    try:
        txt1 = driver.find_element_by_xpath("//span[@class='plButton-label.v-ellipsis']")
        print(txt1)
        print('You need to login, close browser and restart')
        exit()  # leaves browser open for login
    except error.NoSuchElementException as e:
        print(e)


def dismiss_sign_up(driver):
    dismiss: bool = driver.find_element_by_css_selector("input[type='submit']") \
                    and item.find_element_by_css_selector("title[type='Sign Up']")
    if dismiss:
        item.find_element_by_class_name('c-close-icon.c-modal-close-icon').click()


def go_to_cart(driver):
    cart = 'https://www.bestbuy.com/cart'
    driver.get(cart)
    remove_other_items(driver)


def add_to_cart(driver):
    found: bool = False
    while not found:
        print(datetime.datetime.now())
        try:
            # TODO - Need a better condition to check 'add-to-cart' button
            cart = driver.find_element_by_class_name('c-button-primary') \
                   and driver.find_element_by_class_name('add-to-cart-button')
            print('Add-to-cart available', cart.text)
            for items in driver.find_elements_by_class_name('product-data-value.body-copy'):
                print('You are buying:', items.text)
            cart.click()
            print('Clicked Add-to-cart button')
            # This is probably redundant coz of go_to_cart function but better to check
            go_to_cart_button = WebDriverWait(driver, 10).until(
                expect.presence_of_element_located((By.CLASS_NAME, 'go-to-cart-button')))
            go_to_cart_button.click()
            print('FOUND FOUND FOUND')
            found = True
        except error.NoSuchElementException:
            print('>>>Add-to-cart NOT available')
            time.sleep(600)
            item.refresh()
        except error.ElementClickInterceptedException:
            # TODO - This will still not add item in cart
            print('Checking if it is survey popup')
            survey_check(driver)
            dismiss_sign_up(driver)


def do_checkout(driver):
    try:
        checkout = WebDriverWait(driver, 10).until(
            expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-primary')))
        checkout.click()
    except error.TimeoutException:
        print('Checkout button not found- Timeout Exception')
        print('check if continue to payment button exists')


def signed_in_check(driver):
    # Are you signed-in to complete payment
    try:
        payment_info = WebDriverWait(driver, 4). \
            until(expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-secondary')))
        payment_info.click()
    except error.NoSuchElementException:
        print('perhaps card information is already available')
        pass


def text_message(msg: str, my_url: str, sid, token, frm, whom):
    try:
        # account_sid = sid
        # auth_token = token
        client = Client(sid, token)
        my_msg = str(msg + ' ' + my_url)
        message = client.messages.create(from_=frm, body=my_msg, to=whom)
        print(message.sid)
    except TwilioRestException as err:
        print(err)


def login_and_pay(driver):
    try:
        email = WebDriverWait(driver, 6).until(expect.presence_of_element_located((By.ID, 'fld-e')))
        email.clear()
        email.send_keys(my_email)
    except error.TimeoutException:
        print('Timeout error - email/login prefilled or already signed in or not available. Checking...')
        try:
            WebDriverWait(driver, 4).until(
                expect.presence_of_element_located((By.CLASS_NAME, 'v-fw-medium.prefilled-label')))
            correct_email = driver.find_element_by_class_name('prefilled-value').text
            if str(correct_email.strip()) != str(my_email.strip()):
                print('check email manually, process should fail now', correct_email, my_email)
            else:
                print('found correct email', correct_email)
        except error.TimeoutException:
            print('perhaps already signed-in?')
            # TODO - TEST & remove signed_in_check method call if not needed
            # signed_in_check(driver)
        except error.NoSuchElementException:
            print('what did i forget now')
    except error.NoSuchElementException:
        print('No such element - email')

    try:
        password = WebDriverWait(driver, 6).until(expect.presence_of_element_located((By.ID, 'fld-p1')))
        password.clear()
        password.send_keys(my_password)
        try:
            # Sign-in does not work because password/email is wrong(Thrown when testing at school...not sure why)
            # continue_as_guest = driver.find_element_by_css_selector(
            #     'button[class = "c-button.c-button-secondary.c-button-lg.cia-guest-content__continue guest"]')
            # continue_as_guest.click()
            sign_in = driver.find_element_by_class_name(
                'c-button.c-button-secondary.c-button-lg.c-button-block.c-button-icon.'
                'c-button-icon-leading.cia-form__controls__submit ')
            sign_in.click()
            try:
                driver.find_element_by_class_name('c-alert-content')
                print('***The password was incorrect.***')
            except error.NoSuchElementException:
                print('This is NOT incorrect password exception')
        except error.NoSuchElementException:
            print('No password field found, already signed in')
    except error.TimeoutException:
        print('Timeout error - password prefilled or not available')

    try:
        continue_to_pay_button = WebDriverWait(driver, 6). \
            until(expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-secondary')))
        continue_to_pay_button.click()
    except error.TimeoutException:
        print('Continue to Payment Information button not found')
    finally:
        # Send msg before placing order
        text_message('Waiting for Payment', 'https://www.bestbuy.com/checkout/r/payment',
                     account_sid, auth_token, f_ph, t_ph)

# TODO - FIND HOW TO INPUT VERIFICATION CODE FROM GMAIL
# Necessary because sometimes appears after signing in


def verify(driver):
    try:
        verification_code = WebDriverWait(driver, 6). \
            until(expect.presence_of_element_located((By.CSS_SELECTOR, 'input[id = "verificationCode"]')))
        verification_code.send_keys(verification_code)
        verification_code.send_keys(Keys.RETURN)
    except error.TimeoutException as err:
        print(err)


def payment_information(driver):
    try:
        # driver.get('https://www.bestbuy.com/checkout/r/payment')
        credit_card = driver.find_element_by_css_selector('input[id = "optimized-cc-card-number"]')
        credit_card.send_keys(credit_card)

        first_name = driver.find_element_by_css_selector('input[id = "firstName"]')
        first_name.send_keys(f_name)

        last_name = driver.find_element_by_css_selector('input[id = "lastName"]')
        last_name.send_keys(l_name)

        address = driver.find_element_by_css_selector('input[id = "street"]')
        address.send_keys(address)

        street = driver.find_element_by_css_selector('input[id = "city"]')
        street.send_keys(city)

        st = driver.find_element_by_css_selector('select[id = "state"]')
        st.send_keys(state)
        st.send_keys(Keys.RETURN)

        zip_cd = driver.find_element_by_css_selector('input[id = "zipcode"]')
        zip_cd.send_keys(zip_code)
    except error.NoSuchElementException as err:
        print(err)


def place_your_order(driver, test):
    if test != 'TEST':
        try:
            driver.find_element_by_css_selector(
                'button[class = "btn.btn-lg.btn-block.btn-primary"]').click()
        except error.NoSuchElementException as err:
            print(err)
    else:
        print('No order placed - TESTING')


def remove_other_items(driver):
    # Gets rid of all other items in cart
    # IN PROGRESS
    try:
        # driver.get('https://www.bestbuy.com/cart')
        item_list = WebDriverWait(driver, 6).until(
            expect.presence_of_element_located((By.CSS_SELECTOR, 'ul[class = "item-list"]')))
        items = item_list.find_elements_by_css_selector('section[class = "card"]')
        # print(len(items))
        for itm in items:
            # print(itm.get_attribute("auto-test-sku"))
            remove_button = itm.find_element_by_css_selector('a[title = "Remove"]')
            if itm.get_attribute("auto-test-sku") != '6424521':
                remove_button.click()
                # driver.refresh()
                time.sleep(2)
                # item_remove = WebDriverWait(driver, 6).until(
                # expect.presence_of_element_located((By.CSS_SELECTOR, 'div[class = "fluid_item_actions"]')))
                # remove_button = WebDriverWait(driver, 6).until(
                # expect.presence_of_element_located((By.CSS_SELECTOR, 'a[title = "Remove"]').By.CSS))
                # remove_button.click()
                # correct_product = WebDriverWait(driver, 6).until(expect.presence_of_element_located(
                #     (By.CSS_SELECTOR, 'div[auto-test-sku = "6424521"]')))
                # correct_product = driver.find_element_by_css_selector('div[auto-test-sku = "6424521"]')
                # sku_num = correct_product.get_attribute("auto-test-sku")
                # print("No")
    except (error.TimeoutException, error.NoSuchElementException) as err:
        print(err)


def queue_check(driver):
    while True:
        try:
            queue = WebDriverWait(driver, 6).until(
                expect.element_to_be_clickable((By.CSS_SELECTOR, '.add-to-cart-button')))
            queue.click()
            break
        except TimeoutError:
            item.refresh()
            # TODO - check if we can find a better element during queued
            # driver.find_element_by_css_selector
            pass


# MAIN CODE STARTS HERE


item = load(site)  # open browser and go to product page

login_check(item)
online_deal(item)
survey_check(item)
add_to_cart(item)
go_to_cart(item)
do_checkout(item)
login_and_pay(item)
payment_information(item)

# uncomment below and remove test if final code
# place_your_order(item, 'TEST')
