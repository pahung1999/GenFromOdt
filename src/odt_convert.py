from datetime import datetime, timedelta
import random
from odf import text, teletype
import random
from faker import Faker
import locale


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
            print(
                f"Fail to delete child node when replace {pattern} -> {repl}")
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

def gen_info(KEY_LIST):
    """
    Generate replacement information based on the provided KEY_LIST.

    Args:
        KEY_LIST (list): The list of keys to generate information for.

    Returns:
        dict: A dictionary containing the generated replacement information.
    """

    KEY_LIST_1 = ["contract_no", 
             "contract_date", 
             "seller_company", 
             "seller_address", 
             "buyer_company",
             "specifications",
             "quantity",
             "unit_price",
             "total_value",
             "time_of_shipment",
             ]

    if KEY_LIST == KEY_LIST_1:

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
                "seller_address": f"{fake1.address().upper()}", 
                "buyer_company": f"{fake2.company()}",
                "specifications" : "As Per PS-96 Standard",
                "quantity": random.choice(['SAME AS ABOVE: + / - 5%', f'{random.randint(10, 5000)} MT']),
                "unit_price": random.choice(['USD SAME AS ABOVE', f'USD {random.randint(100, 1000)}.00/MT']),
                "total_value": f'USD {usd_string}',
                "time_of_shipment": f"{time_of_shipment}"
            }
        return replace_dict
    
    return {}