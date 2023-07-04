from datetime import datetime, timedelta
import random
from odf import text, teletype
import random
from faker import Faker
import locale
import inflect


def replace_text_single(Elem, item, pattern, repl):
    """
    Replace a single occurrence of a pattern with a replacement string in a text element.

    Args:
        Elem (odf.Element): The type of text element (e.g., text.H, text.P, text.Span).
        item (odf.Element): The text element to be modified.
        pattern (str): The pattern to search for.
        repl (str): The replacement string.

    Returns:
        odf.Element: The modified text element.
    """
    s = teletype.extractText(item)
    if s.find(pattern) != -1:
        # repl = get_format(pattern)(repl)
        s = s.replace(pattern, repl)
        new_item = Elem()
        new_item.setAttribute('stylename', item.getAttribute('stylename'))
        new_item.addText(s)
        item.parentNode.insertBefore(new_item, item)
        try:
            # Sometime, the text is replaced in the parent node
            # But not updated in the child node
            item.parentNode.removeChild(item)
        except Exception:
            # print_exc()
            error = f"Fail to delete child node when replace {pattern} -> {repl}"
            # print(
            #     f"Fail to delete child node when replace {pattern} -> {repl}")
        return new_item
    else:
        return item

def replace_text(node, k, v):
    """
    Replace occurrences of a pattern with a replacement string in a given node.

    Args:
        node (odf.Element): The parent node containing text elements.
        k (str): The pattern to search for.
        v (str): The replacement string.

    Returns:
        odf.Element: The modified parent node.
    """

    elements = [text.H, text.P, text.Span]
    for Elem in elements:
        for elem in node.getElementsByType(Elem):
            if k in str(elem):
                elem = replace_text_single(Elem, elem, k, str(v))
    return node

def gen_shipment_date():
    """
    Generate a random shipment date (date_X) and calculate the date after 3 months (date_Y).

    Returns:
        tuple: A tuple containing the shipment dates (date_X and date_Y) in the format "%m/%d/%Y".
    """
    # Generate random date X
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2023, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    date_X = random_date.strftime("%m/%d/%Y")

    # Calculate date Y after 3 months
    date_X_datetime = datetime.strptime(date_X, "%m/%d/%Y")
    date_Y = (date_X_datetime + timedelta(days=3*30)).strftime("%m/%d/%Y")
    return date_X, date_Y

def gen_code_string(code_temp):
    """
    Generate a code string based on a template.

    The template contains the characters 'T' and 'N'. The 'T' character will be replaced
    with a random uppercase letter from the alphabet (A-Z), and the 'N' character will be
    replaced with a random digit (0-9). Any other characters in the template will be kept
    unchanged in the resulting code string.

    Args:
        code_temp (str): The code template.

    Returns:
        str: The generated code string.

    Example:
        >>> generate_code_string("TN-NT")
        'P3-9C'
    """
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'

    string_value = []
    for char in code_temp:
        if char == "T":
            string_value.append(random.choice(letters))
        elif char == "N":
            string_value.append(random.choice(numbers))
        else:
            string_value.append(char)
    code_string = ''.join(string_value)
    return code_string

def gen_add_info(add_temp, max_len=20, min_len = 1, upper=True):
    """
    Generate additional information based on a template.

    The function replaces placeholders in the template with randomly generated values using
    the Faker library. The placeholders are defined as follows:
    - "(address)": Replaced with a randomly generated address.
    - "(country)": Replaced with a randomly generated country.
    - "(city)": Replaced with a randomly generated city.
    - "(company)": Replaced with a randomly generated company name.
    - "(name)": Replaced with a randomly generated name.

    The generated information is returned as a string. If the length of the generated string
    exceeds the specified maximum length or if the generated string is the same as the original
    template, the function will generate a new string until the conditions are met.

    Args:
        add_temp (str): The template for additional information.
        max_len (int, optional): The maximum length of the generated string. Defaults to 20.
        upper (bool, optional): Whether to convert the generated values to uppercase. Defaults to True.

    Returns:
        str: The generated additional information.

    Example:
        >>> gen_add_info("Contact: (name), Company: (company), Address: (address)")
        'Contact: John Doe, Company: ABC Corporation, Address: 123 Main St'
    """
    fake = Faker()
    new_add = add_temp
    while new_add == add_temp or len(new_add) > max_len or len(new_add) < min_len:
        new_add = add_temp
        if "(address)" in add_temp:
            fake_address = fake.street_address() + ", " + fake.city() + ", " + fake.country()
            if upper:
                new_add = new_add.replace("(address)", fake_address.upper())
            else:
                new_add = new_add.replace("(address)", fake_address)
        if "(country)" in add_temp:
            if upper:
                new_add = new_add.replace("(country)", fake.country().upper())
            else:
                new_add = new_add.replace("(country)", fake.country())
        if "(city)" in add_temp:
            if upper:
                new_add = new_add.replace("(city)", fake.city().upper())
            else:
                new_add = new_add.replace("(city)", fake.city())
        if "(company)" in add_temp:
            if upper:
                new_add = new_add.replace("(company)", fake.company().upper())
            else:
                new_add = new_add.replace("(company)", fake.company())
        if "(name)" in add_temp:
            if upper:
                new_add = new_add.replace("(name)", fake.name().upper())
            else:
                new_add = new_add.replace("(name)", fake.name())
        if "(email)" in add_temp:
            if upper:
                new_add = new_add.replace("(email)", fake.email().upper())
            else:
                new_add = new_add.replace("(email)", fake.email())
    return new_add


def convert_number_to_text(number):
    """
    Convert a number to its textual representation.

    The function uses the `inflect` library to convert the given number into its corresponding
    textual representation. The textual representation is returned as a string, with each word
    capitalized.

    Args:
        number (int): The number to be converted.

    Returns:
        str: The textual representation of the number.

    Example:
        >>> convert_number_to_text(123)
        'ONE HUNDRED TWENTY-THREE'
    """
    p = inflect.engine()
    text = p.number_to_words(number).upper()
    return text

def generate_random_words(min_len=5, max_len=50):
    """
    Generate a random string consisting of random words.

    The function uses the `Faker` library to generate random words and concatenates them into
    a string. The generated string will have a length between `min_len` and `max_len`.

    Args:
        min_len (int, optional): The minimum length of the generated string. Defaults to 5.
        max_len (int, optional): The maximum length of the generated string. Defaults to 50.

    Returns:
        str: The generated string consisting of random words.

    Example:
        >>> generate_random_words()
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    """
    fake = Faker()
    words_list = [fake.word() for _ in range(random.randint(1, 100))]
    words = " ".join(words_list)
    while len(words) < min_len or len(words) > max_len:
        words_list = [fake.word() for _ in range(random.randint(1, 100))]
        words = " ".join(words_list)
    return words

def multiply_strings(x, y):
    # Convert strings to numerical values
    x_value = float(x.replace(',', ''))
    y_value = float(y.replace(',', ''))
    
    # Perform multiplication
    result = x_value * y_value
    
    # Format the result back into string format
    result_string = "{:,.2f}".format(result)
    
    return result_string

def check_replace_key(replace_dict, replace_key):
    for key in replace_key:
        if key not in replace_dict:
            print(f"Warning: replace_dict missing {key}")

def gen_info(key_name: str, replace_key: str):
    """
    Generate replacement information based on the provided KEY_LIST.

    Args:
        key_name (str): Name of key list (in key_dict.json)

    Returns:
        dict: A dictionary containing the generated replacement information.
    """

    if key_name == "sale_contract":

        contract_date, time_of_shipment = gen_shipment_date()

        #Gen company and address
        fake1 = Faker()
        fake2 = Faker()

        #Gen USD money
        # Set the locale to United States (English)
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Generate random USD strings from $1.00 to $999,999.00
        usd_string = locale.currency(random.randint(1, 1000000), symbol=True, grouping=True)

        replace_dict = replace_dict = {
                "contract_no" : f"RH{str(random.randint(0000000, 9999999)).zfill(7)}HN", 
                "contract_date": f"{contract_date}", 
                "seller_company": f"{fake1.company()}", 
                "seller_address": f"{fake1.address().upper()}".replace("\n"," "), 
                "buyer_company": f"{fake2.company()}",
                "specifications" : "As Per PS-96 Standard",
                "quantity": random.choice(['SAME AS ABOVE: + / - 5%', f'{random.randint(10, 5000)} MT']),
                "unit_price": random.choice(['USD SAME AS ABOVE', f'USD {random.randint(100, 1000)}.00/MT']),
                "total_value": f'USD {usd_string}',
                "time_of_shipment": f"{time_of_shipment}"
            }
        
        check_replace_key(replace_dict, replace_key)
        return replace_dict
    
    if key_name == "bill_of_lading":
        port1 = gen_add_info("(city),(country)", max_len=20, upper=True)
        port2 = gen_add_info("(city),(country)", max_len=20, upper=True)
        port3 = gen_add_info("(city),(country)", max_len=20, upper=True)


        start_date = datetime.now() - timedelta(days=365)  # Adjust the range of dates if needed
        end_date = datetime.now()

        random_date = start_date + (end_date - start_date) * random.random()
        date_str = random_date.strftime("%B %d, %Y")

        replace_dict  = {
            "bill_id" :  gen_code_string("TTTTTTTNNNNNNN"),
            "company1.1" : gen_add_info("(company) INC. C/O", max_len=40, upper=True),
            "company1.2" : gen_add_info("(company) CO.,LTD.", max_len=40, upper=True),
            "address1" : gen_add_info("(address)", max_len=80, upper=True),
            "company2" : gen_add_info("(company) CO LTD", max_len=35, upper=True),
            "address2" : gen_add_info("(address)", max_len=80, upper=True),
            "code1": gen_code_string("NNNNNNNNNN"), "code2": gen_code_string("NN/TTT-TTTTT"), "code3": gen_code_string("NNNTT/TTT-TTTT"),
            "place_of_receipt": port1, "place_of_delivery": port2,
            "ocean_vessel": gen_add_info("(name)", max_len=18, upper=True), "voyage_no": gen_code_string("NNNNT"), 
            "flag": gen_add_info("(country)", max_len=15, upper=True),
            "port_of_loading": port1, "port_of_discharge": port2,
            "bale_quantity": str(random.randint(10,999)), 
            "gross_weight": "{:,.3f}".format(random.randint(1, 999999)),
            "measurement": "{:,.3f}".format(random.randint(1, 9999)),
            "country1": gen_add_info("(country)", max_len=20, upper=True), 
            "tel1": gen_code_string("NNN-NNNNNNNN"), "fax1": gen_code_string("NNN-NNNNNNNN"), 
            "name_contact1":  gen_add_info("(name)", max_len=20, upper=True), 
            "ein_tax1": "SH_EIN_"+gen_code_string("NN-NNNNNNN"),
            "country2": gen_add_info("(country)", max_len=20, upper=True), 
            "tel2": gen_code_string("NNN-NNNNNNNN"), "fax2": gen_code_string("NNN-NNNNNNNN"), 
            "name_contact2": gen_add_info("(name)", max_len=20, upper=True), 
            "gmail2": gen_add_info("(email)", max_len=20, upper=True),
            "freight_prepaid_at": port3, "place_of_issue": port3, "date": date_str
        }

        con_quantity = random.randint(1, 5)
        replace_dict['con_quantity'] = str(con_quantity)
        replace_dict['text_con_quantity'] = convert_number_to_text(con_quantity)
        con_no = gen_code_string("NNTT")

        for i in range(5):
            if i+1 <= con_quantity:
                replace_dict[f'con_no{i+1}'] = con_no
                replace_dict[f'con_num{i+1}'] = gen_code_string("TTTTNNNNNNN/")
                replace_dict[f'con_mark{i+1}'] = gen_code_string("TTTNNNNNN")
            else:
                replace_dict[f'con_no{i+1}'] = " "
                replace_dict[f'con_num{i+1}'] = " "
                replace_dict[f'con_mark{i+1}'] = " "

        check_replace_key(replace_dict, replace_key)
        return replace_dict

    if key_name == "commercial_invoice":
        start_date = datetime(2000, 1, 1)
        end_date = datetime.now()

        quantity = "{:,.3f}".format(random.randint(1, 1000))
        unit_price = "{:,.2f}".format(random.randint(1, 500))
        amount = multiply_strings(quantity, unit_price)

        random_date = start_date + random.random() * (end_date - start_date)
        date_string = random_date.strftime("%m/%d/%Y")
        replace_dict = {
            "seller_company": gen_add_info("(company) Co.,Ltd.", max_len=40, min_len = 10, upper=False),
            "seller_address": gen_add_info("(address)", max_len=40, min_len = 10, upper=True),
            "seller_tel": gen_code_string("NNN-NNNNNNNN"), "seller_fax": gen_code_string("NNN-NNNNNNNN"),
            "buyer_company": random.choice([gen_add_info("(company) Co.,Ltd.", max_len=40, min_len = 10, upper=True), gen_add_info("(company) INC. C/O", max_len=40, min_len = 10, upper=True)]),
            "buyer_address": gen_add_info("(address)", max_len=40, min_len = 10, upper=True),
            "invoice_id": gen_code_string("NNNNNNNN"), "invoice_date": date_string,
            "product": generate_random_words(min_len=15, max_len=80).upper(),
            "quantity": quantity, "unit_price": unit_price, "amount": amount,
            "contract_no": gen_code_string("TTNNNNNNNTT"), "sailing_date": date_string,
            "loading_port": gen_add_info("(city) (country)", max_len=40, min_len = 10, upper=True),
            "discharge_port": gen_add_info("(city) (country)", max_len=40, min_len = 10, upper=True),
        }
        check_replace_key(replace_dict, replace_key)
        return replace_dict
    
    if key_name == "packing_list":

        start_date = datetime(2000, 1, 1)
        end_date = datetime.now()
        random_date = start_date + random.random() * (end_date - start_date)
        date_string = random_date.strftime("%m/%d/%Y")

        container_quantity = random.randint(1, 9)

        replace_dict = {
            "seller_company": gen_add_info("(company) Co.,Ltd.", max_len=40, min_len = 20, upper=False),
            "seller_address": gen_add_info("(address)", max_len=150, min_len = 30, upper=True),
            "seller_tel": gen_code_string("NNN-NNNNNNNN"), "seller_fax": gen_code_string("NNN-NNNNNNNN"),
            "buyer_company": random.choice([gen_add_info("(company) Co.,Ltd.", max_len=50, min_len = 10, upper=True), gen_add_info("(company) INC. C/O", max_len=40, min_len = 10, upper=True)]),
            "buyer_tel": gen_code_string("NN-NNNNNNNN-NNNNNN"), "buyer_fax": gen_code_string("NN-NNNN-NNNNNNN"),
            "buyer_address": gen_add_info("(address)", max_len=150, min_len = 30, upper=True),
            "invoice_id": gen_code_string("NNNNNNNN"), "invoice_date": date_string,
            "product": generate_random_words(min_len=40, max_len=120).upper(),
            "contract_no": gen_code_string("TTNNNNNNNTT"),
            "container_quantity": str(container_quantity),
        }

        total_g = 0
        total_n = 0
        total_bale = 0
        for i in range(9):
            if i+1 <= container_quantity:
                replace_dict[f'container_num{i+1}'] = gen_code_string("TTTTNNNNNNN")

                g_weight = round(random.uniform(1, 150), 3)
                total_g+=g_weight
                replace_dict[f'g_weight{i+1}'] = "{:,.3f}".format(g_weight)
                
                n_weight = round(random.uniform(1, 150), 3)
                total_n+=n_weight
                replace_dict[f'n_weight{i+1}'] = "{:,.3f}".format(n_weight)

                bale = random.randint(1, 100)
                total_bale+=bale
                replace_dict[f'bale{i+1}'] = str(bale)

            else:
                replace_dict[f'container_num{i+1}'] = ""
                replace_dict[f'g_weight{i+1}'] = ""
                replace_dict[f'n_weight{i+1}'] = ""
                replace_dict[f'bale{i+1}'] = ""

        replace_dict['total_g'] = "{:,.3f}".format(total_g)
        replace_dict['total_n'] = "{:,.3f}".format(total_n)
        replace_dict['total_bale'] = str(total_bale)

        check_replace_key(replace_dict, replace_key)
        return replace_dict
    return {}