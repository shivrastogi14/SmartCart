import configparser


def config_read(file, tld, scope):
    param_obj = {}
    config = configparser.ConfigParser()
    config.read(file)
    if scope == 'all':
        t_ph = config['TWILIO']['t_ph']
        f_ph = config['TWILIO']['f_ph']
        account_sid = config['TWILIO']['account_sid']
        auth_token = config['TWILIO']['auth_token']
        param_obj.update({'t_ph': t_ph, 'f_ph': f_ph, 'account_sid': account_sid, 'auth_token': auth_token})
    f_name = config[tld]['first_name']
    l_name = config[tld]['last_name']
    address = config[tld]['address']
    city = config[tld]['city']
    state = config[tld]['state']
    zip_code = config[tld]['zip_code']
    ph = config[tld]['phone']
    cc_number = config[tld]['credit_card']
    cvv = config[tld]['verification_code']
    my_email = config[tld]['email']
    my_password = config[tld]['password']
    param_obj.update({'f_name': f_name, 'l_name': l_name, 'address': address, 'city': city,
                      'state': state, 'zip_code': zip_code, 'ph': ph, 'cc_number': cc_number,
                      'my_email': my_email, 'my_password': my_password, 'cvv': cvv})
    return param_obj


def first_time_param(file, tld):
    config = configparser.ConfigParser()
    print('It seems you have not shopped on this site before')
    print('Bot requires email/password to validate login for new site', tld)
    email = input('Please enter your email:= ').strip()
    password = input('Please enter your password:=').strip()
    payment = input('Would you like bot to attempt payment:=').strip().lower()
    sms = input('Would you like bot to send texts via Twilio:=').strip().lower()

    config['DEFAULT'] = {}
    config[tld] = {}
    site = config[tld]
    site['email'] = email
    site['password'] = password

    if payment == 'y':
        first_name = input('Enter your first name:=').strip()
        last_name = input('Enter your last name:=').strip()
        street = input('Enter your street address[apt # goes here]:=').strip()
        city = input('Enter your city:=').strip()
        state = input('Enter your state:=').strip()
        zip_code = input('Enter your zip code[US only]:=').strip()
        phone = input('Enter your phone number:=').strip()
        credit_card = input('Enter your credit card [It is safe]:=').strip()
        cvv = input('Enter your cvv from back of your card [stored only on your PC]:=').strip()
        site['first_name'] = first_name
        site['last_name'] = last_name
        site['address'] = street
        site['city'] = city
        site['state'] = state
        site['zip_code'] = zip_code
        site['phone'] = phone
        site['credit_card'] = credit_card
        site['verification_code'] = cvv
    else:
        print('I understand')

    if sms == 'y':
        t_ph = input('Enter twilio phone number:=').strip()
        f_ph = input('Enter phone to send text to:=').strip()
        sid = input('Enter your SID provided by twilio:=').strip()
        token = input('Enter token provided by twilio:=').strip()
        config['TWILIO'] = {
            't_ph': t_ph,
            'f_ph': f_ph,
            'account_sid': sid,
            'auth_token': token
        }
    else:
        print('Sure, no text would be sent')

    with open(file, 'w') as fp:
        fp.write(';*** DON\'T MODIFY MANUALLY ***'+'\n')
        config.write(fp)
