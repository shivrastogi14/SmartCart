import os
import configparser

driver_location = r'F:\Chromium\\'
# os.environ['PATH'] += ';driver_location;'

tld = 'bestbuy'

credentials = os.path.join(driver_location, tld)
if not os.path.exists(credentials):
    os.mkdir(credentials)

# absolute path to filename
filename = os.path.join(credentials+'\\parameters')
print(filename)


def config_write(file):
    # Change to config directory
    os.chdir(credentials)
    config = configparser.ConfigParser()
    config['DEFAULT'] = {}
    config['TWILIO'] = {
        't_ph': '+16073005373',
        'f_ph': '6093757847',
        'account_sid': 'ACbe38fb725e86c886f7142170a544892f',
        'auth_token': '6bcbe8b59aa78018abd4a0b90bdea1dc'
        }
    config[tld] = {}
    site = config[tld]
    site['email'] = 'rrastogi@comcast.net'
    site['password'] = 'Up1nlefyab'
    site['credit_card'] = ''
    site['first_name'] = 'Rishi'
    site['last_name'] = "Rastogi"
    site['address'] = '2 Cambridge Way'
    site['city'] = 'West Windsor'
    site['state'] = 'NJ'
    site['zip_code'] = '08550'
    site['verification_code'] = ''
    site['phone'] = '609-716-6156'
    site['member_number'] = '5173009485'
    site['account_sid'] = 'ACbe38fb725e86c886f7142170a544892f'
    site['auth_token'] = '6bcbe8b59aa78018abd4a0b90bdea1dc'
    with open(file, 'w') as fp:
        fp.write(';*** DON\'T MODIFY MANUALLY ***'+'\n')
        config.write(fp)


def config_read(file):
    os.chdir(credentials)
    config = configparser.ConfigParser()
    config.read(file)
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
    return t_ph, f_ph, f_name, l_name, add, city, state, zip_code, ph, membership, cc_number, account_sid,\
           auth_token, my_email, my_password

# config_write(filename)
config_read(filename)

# print(config.sections())
# print(t_ph, f_ph, f_name, l_name, add, city, state, zip_code, ph, membership, cc_number)
