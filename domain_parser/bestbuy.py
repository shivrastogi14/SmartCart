# TODO - add Logger
# TODO - add debug to output extra data
# TODO - parse product link passed to compare SKU (should always be same)
# TODO - create a secrets file for sensitive information
# TODO - stop computer from going to sleep
# TODO - Test workaround for signUp dialog box
# TODO - Some items are only limited to 3 per order and this is not handled in method add-to-cart

import os
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


class BestBuy:
    def __init__(self, uri: str, refresh_timer=600, **kwargs):
        # TODO: remove dependency on global param_obj
        self.uri = uri
        self.param_obj = kwargs
        self.refresh_timer = refresh_timer

    def load(self, uri=None):
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
        driver.get(self.uri)
        # print(driver.get_cookies())  # print to LOG when debug is ON
        return driver

    def online_deal(self, driver):
        # Just for checking if it is online only or best buy brand
        try:
            badge_item = driver.find_element(By.CSS_SELECTOR, 'img[class = "badge-image"]')
            type_of_badge = badge_item.get_attribute('alt')
            print(type_of_badge)
        except error.NoSuchElementException:
            print('No Badge')
            # TODO - update zip code to point to correct store

    def survey_check(self, driver):
        # wait for survey alert/popup to load and switch to it
        # else add to cart will fail coz add-to-cart button is not clickable
        # selenium.common.exceptions.ElementClickInterceptedException
        try:
            WebDriverWait(driver, 5).until(expect.presence_of_element_located((By.ID, 'survey_invite_no')))
            click_no = driver.find_element(By.ID, 'survey_invite_no')
            click_no.click()
        except (error.TimeoutException, error.NoSuchElementException):
            print('Survey element not found')

    def login_check(self, driver, pay: bool):
        if pay is False:
            try:
                txt1 = driver.find_element(By.CSS_SELECTOR, 'button[data-lid = "hdr_signin"]')
                # txt1 = driver.find_element_by_css_selector('button[data-lid = "hdr_signin"]')
                if txt1.text == "Account":
                    print('You need to login...Logging in now')
                    txt1.click()
                    WebDriverWait(driver, 4).until(expect.presence_of_element_located((
                        By.CSS_SELECTOR, 'a[data-lid = "ubr_mby_signin_b"]'))).click()
                    self.login(driver, 1)
                else:
                    print("Already logged in")
            except error.NoSuchElementException as e:
                print(e)
        elif pay is True:
            try:
                WebDriverWait(driver, 4).until(
                    expect.presence_of_element_located((By.CLASS_NAME, 'v-fw-medium.prefilled-label')))
                self.login(driver, 0)
            except error.TimeoutException:
                print('You may need to login...trying to login now')
                self.login(driver, 1)

    def login(self, driver, initial: int):
        my_email = self.param_obj.get('my_email')
        my_password = self.param_obj .get('my_password')
        try:
            if initial == 1:
                email = WebDriverWait(driver, 6).until(
                    expect.presence_of_element_located((By.CSS_SELECTOR, 'input[id = "fld-e"]')))
                email.clear()
                email.send_keys(my_email)
            password = WebDriverWait(driver, 6).until(
                expect.presence_of_element_located((By.CSS_SELECTOR, 'input[id = "fld-p1"]')))
            password.clear()
            password.send_keys(my_password)
            driver.find_element(By.CSS_SELECTOR, 'button[data-track = "Sign In"]').click()
        except (error.TimeoutException, error.NoSuchElementException) as e:
            print(e)

    def dismiss_sign_up(self, driver):
        dismiss: bool = driver.find_element(By.CSS_SELECTOR, "input[type='submit']") \
                        and driver.find_element(By.CSS_SELECTOR, "title[type='Sign Up']")
        if dismiss:
            driver.find_element(By.CLASS_NAME, 'c-close-icon.c-modal-close-icon').click()

    def go_to_cart(self, driver):
        cart = 'https://www.bestbuy.com/cart'
        driver.get(cart)
        self.remove_other_items(driver)

    def add_to_cart(self, driver, timer):
        found: bool = False
        while not found:
            print(datetime.datetime.now())
            try:
                # TODO - Need a better condition to check 'add-to-cart' button
                cart = driver.find_element(By.CLASS_NAME, 'c-button-primary') \
                       and driver.find_element(By.CLASS_NAME, 'add-to-cart-button')
                print('Add-to-cart available - button label is:=', cart.text)
                for items in driver.find_elements(By.CLASS_NAME, 'product-data-value.body-copy'):
                    print('You are buying:', items.text)
                cart.click()
                print('Clicked Add-to-cart button')
                # This is probably redundant coz of go_to_cart function but better to check
                go_to_cart_button = WebDriverWait(driver, 10).until(
                    expect.presence_of_element_located((By.CLASS_NAME, 'go-to-cart-button')))
                go_to_cart_button.click()
                found = True
            except error.NoSuchElementException:
                print('>>>Add-to-cart NOT available')
                time.sleep(timer)
                driver.refresh()
            except error.ElementClickInterceptedException:
                # TODO - This will still not add item in cart
                print('Checking if it is survey popup')
                self.survey_check(driver)
                self.dismiss_sign_up(driver)

    def do_checkout(self, driver):
        try:
            checkout = WebDriverWait(driver, 10).until(
                expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-primary')))
            checkout.click()
        except error.TimeoutException:
            # TODO: handle click interception, it can occur if more than 1 item in cart
            print('Checkout button not found- Timeout Exception')
            print('check if continue to payment button exists')

    def signed_in_check(self, driver):
        # Are you signed-in to complete payment
        try:
            payment_info = WebDriverWait(driver, 4). \
                until(expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-secondary')))
            payment_info.click()
        except error.NoSuchElementException:
            print('perhaps card information is already available')
            pass

    def text_message(self, msg: str, my_url: str, sid, token, frm, whom):
        try:
            client = Client(sid, token)
            my_msg = str(msg + ' ' + my_url)
            message = client.messages.create(from_=frm, body=my_msg, to=whom)
            print(message.sid)
        except TwilioRestException as err:
            print(err)

    def login_and_pay(self, driver):
        account_sid = self.param_obj.get('account_sid')
        auth_token = self.param_obj.get('auth_token')
        f_ph = self.param_obj.get('f_ph')
        t_ph = self.param_obj.get('t_ph')
        try:
            continue_to_pay_button = WebDriverWait(driver, 6).until(
                expect.presence_of_element_located((By.CLASS_NAME, 'btn.btn-lg.btn-block.btn-secondary')))
            continue_to_pay_button.click()
            print('Clicked Continue to Payment Information button')
            self.text_message('Waiting for Payment', 'https://www.bestbuy.com/checkout/r/payment',
                              account_sid, auth_token, f_ph, t_ph)
        except error.TimeoutException:
            print('Continue to Payment Information button not found')
            self.login_check(driver, True)
            # TODO: can it create an infinite recursion ?
            self.login_and_pay(driver)

    # TODO - FIND HOW TO INPUT VERIFICATION CODE FROM GMAIL
    # Necessary because sometimes verify appears after signing in

    def verify(self, driver):
        try:
            verification_code = WebDriverWait(driver, 6). \
                until(expect.presence_of_element_located((By.CSS_SELECTOR, 'input[id = "verificationCode"]')))
            verification_code.send_keys(verification_code)
            verification_code.send_keys(Keys.RETURN)
        except error.TimeoutException as err:
            print(err)

    def payment_information(self, driver):
        cc_number = self.param_obj.get('cc_number')
        f_name = self.param_obj.get('f_name')
        l_name = self.param_obj.get('l_name')
        addr = self.param_obj.get('address')
        city = self.param_obj.get('city')
        state = self.param_obj.get('state')
        zip_code = self.param_obj.get('zip_code')
        try:
            driver.get('https://www.bestbuy.com/checkout/r/payment')
            credit_card = driver.find_element(By.CSS_SELECTOR, 'input[id = "optimized-cc-card-number"]')
            credit_card.send_keys(cc_number)

            first_name = driver.find_element(By.CSS_SELECTOR, 'input[id = "firstName"]')
            first_name.send_keys(f_name)

            last_name = driver.find_element(By.CSS_SELECTOR, 'input[id = "lastName"]')
            last_name.send_keys(l_name)

            address = driver.find_element(By.CSS_SELECTOR, 'input[id = "street"]')
            address.send_keys(addr)

            cty = driver.find_element(By.CSS_SELECTOR, 'input[id = "city"]')
            cty.send_keys(city)

            st = driver.find_element(By.CSS_SELECTOR, 'select[id = "state"]')
            st.send_keys(state)
            st.send_keys(Keys.RETURN)

            zip_cd = driver.find_element(By.CSS_SELECTOR, 'input[id = "zipcode"]')
            zip_cd.send_keys(zip_code)
        except error.NoSuchElementException as err:
            print(err)

    def place_your_order(self, driver, test):
        if test != 'TEST':
            try:
                driver.find_element(By.CSS_SELECTOR, 'button[class = "btn.btn-lg.btn-block.btn-primary"]').click()
            except error.NoSuchElementException as err:
                print(err)
        else:
            print('No order placed - TESTING')

    def remove_other_items(self, driver):
        try:
            item_list = WebDriverWait(driver, 6).until(
                expect.presence_of_element_located((By.CSS_SELECTOR, 'ul[class = "item-list"]')))
            items = item_list.find_elements(By.CSS_SELECTOR, 'section[class = "card"]')
            for itm in items:
                remove_button = itm.find_element(By.CSS_SELECTOR, 'a[title = "Remove"]')
                if itm.get_attribute("auto-test-sku") != '6424521':
                    remove_button.click()
                    time.sleep(2)
                elif itm.get_attribute("auto-test-sku") == '6424521':
                    quantity_button = itm.find_element(By.CSS_SELECTOR, 'select[class = "tb-select"]')
                    quantity_button.send_keys('1')
                    quantity_button.send_keys(Keys.RETURN)
        except error.NoSuchElementException as err:
            print(err)

    def queue_check(self, driver):
        while True:
            try:
                queue = WebDriverWait(driver, 6).until(
                    expect.element_to_be_clickable((By.CSS_SELECTOR, '.add-to-cart-button')))
                queue.click()
                break
            except TimeoutError:
                driver.refresh()
                # TODO - check if we can find a better element during queued
                pass

    def start(self, refresh_timer=600):
        item = self.load(self.uri)  # open browser and go to product page
        self.login_check(item, False)
        self.online_deal(item)
        self.survey_check(item)
        # 600 is for program to wait and refresh again in 10 min
        self.add_to_cart(item, refresh_timer)
        # TODO: if already add to cart then next go_to_cart is not needed
        # bb.go_to_cart(item)
        self.do_checkout(item)
        self.login_and_pay(item)
        self.payment_information(item)
        # uncomment below and remove test if final code
        self.place_your_order(item, 'TEST')
        time.sleep(refresh_timer)


if __name__ == '__main__':
    # MAIN CODE STARTS HERE
    # SETUP GLOBAL VARIABLES
    tld = 'bestbuy'
    driver_location = r'F:\Chromium\\'
    os.environ['PATH'] += f";{driver_location};"
    filename = os.path.join(driver_location, tld, 'parameters.ini')
    # os.environ['PATH'] += r":/Users/shivrastogi/Desktop/Python/:"

    # TODO: based upon text messaging selection by user
    #  change "all" to "None" for NOT reading twilio data
    from config import parameters as pm
    param_obj = pm.config_read(filename, tld, 'all')

    site = 'https://www.bestbuy.com/site/insignia-9-play-charge-usb-c-cable-for-playstation' \
           '-5-white-black/6424521.p?skuId=6424521'
    bb = BestBuy(site, **param_obj)
    item = bb.load(site)  # open browser and go to product page
    bb.login_check(item, False)
    bb.online_deal(item)
    bb.survey_check(item)
    # 600 is for program to wait and refresh again in 10 min
    bb.add_to_cart(item, 600)
    # TODO: if already add to cart then next go_to_cart is not needed
    # bb.go_to_cart(item)
    bb.do_checkout(item)
    bb.login_and_pay(item)
    bb.payment_information(item)
    # uncomment below and remove test if final code
    bb.place_your_order(item, 'TEST')
else:
    print('in bestbuy.py else statement', __name__)
