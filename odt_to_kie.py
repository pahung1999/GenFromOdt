from argparse import ArgumentParser
from odf import opendocument
from src.odt_convert import replace_text
import subprocess
import os
import fitz
from src.pdf_extraction import page_extraction
from src.image_convert import bytes2pillow
from src.get_labelme import labelme_gen


odtin_path = "/home/phung/AnhHung/data/invoice/invoice_CFS/odt_template/demo/sale_contract.odt"
odtout_path = "/home/phung/AnhHung/data/invoice/invoice_CFS/odt_template/demo/temp.odt"
pdf_path = "/home/phung/AnhHung/data/invoice/invoice_CFS/odt_template/demo/temp.pdf"
doc = opendocument.load(odtin_path)

keys_list = ["contract_no", "contract_date", "seller_company", "seller_address", "buyer_company"]

replace_dict = {
    "contract_no" : "RH9230332HN", 
    "contract_date": "03/20/2023", 
    "seller_company": "Hong Kong Chung Nam Trading Co., Ltd", 
    "seller_address": "FLATIRM 01. 8F, NAM FUNG COMMERCIAL CENTRE, NO.19 LAM LOK STREET, KOWLOON BAY, HONGKONG", 
    "buyer_company": "HENG YANG PAPER MILL CO.,LTD"
}

for key in replace_dict:
    replace_text(doc.topnode, f"$({key})", replace_dict[key])
doc.save(odtout_path)    
print("Odt to Odt: Done!")

# Convert ODT to PDF using unoconv
# subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, odtout_path])
subprocess.run(['unoconv', '--format=pdf', '-o', pdf_path, odtout_path])

print("Odt to Pdf: Done!")

labelme_folder = "/home/phung/AnhHung/data/invoice/invoice_CFS/odt_template/demo/labelme/"
pdf_doc = fitz.open(pdf_path)
for page in pdf_doc:
    pixmap = page.get_pixmap()
    image = bytes2pillow(pixmap.tobytes())
    texts, polygons = page_extraction(page, extract_type = "line")
    labelme_gen(polygons, image, 'test', labelme_folder)