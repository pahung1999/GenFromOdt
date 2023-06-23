import argparse
from odf import opendocument
import subprocess
import os
import fitz
from src.odt_convert import replace_text, gen_info
from src.pdf_extraction import page_extraction
from src.image_convert import bytes2pillow
from src.get_label import labelme_gen
import json
from tqdm import tqdm
import copy

KEY_LIST = ["contract_no", 
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

odt_folder = "/home/phung/AnhHung/data/invoice/invoice_CFS/odt_template/"
temp_folder = "./temp"
tempodt_path = "./temp.odt"
temppdf_path = "./temp.pdf"


parser = argparse.ArgumentParser(description='Generate KIE json data from odt template')
parser.add_argument('-n','--samplenum', type=int, help='Number of json each odt template')
parser.add_argument('-o', '--output', type=str, help='Output labelme file')
parser.add_argument('-i','--input', type=str, help='Input odt template folder')

args = parser.parse_args()

odt_folder = args.input

odt_templates = []

pdf_dict = {}
for filename in os.listdir(odt_folder):
    if not filename.endswith("odt"):
        continue
    odtin_path = os.path.join(odt_folder, filename)
    
    # odt_templates.append(doc)
    print(filename)
    template_name = os.path.basename(filename)
    temp_count = 1
    for i in tqdm(range(args.samplenum)):
        doc = opendocument.load(odtin_path)
        replace_dict = gen_info()
        for key in replace_dict:
            replace_text(doc.topnode, f"$({key})", replace_dict[key])
        doc.save(tempodt_path)    

        # Convert ODT to PDF using unoconv
        # subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, odtout_path])
        subprocess.run(['unoconv', '--format=pdf', '-o', temppdf_path, tempodt_path])

        pdf_doc = fitz.open(temppdf_path)
        for page in pdf_doc:
            pixmap = page.get_pixmap()
            image = bytes2pillow(pixmap.tobytes())
            texts, polygons = page_extraction(page, extract_type = "line")
            labelme_gen(polygons, image, f'{template_name}_{temp_count}', args.output)
            temp_count+=1