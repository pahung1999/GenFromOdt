import argparse
from odf import opendocument
import subprocess
import os
import fitz
from tqdm import tqdm
import random
import json
import copy
from src.pdf_extraction import page_extraction
from src.image_convert import bytes2pillow, pillow2base64
from src.get_label import labelme_gen, kie_gen
from src.odt_convert import replace_text, gen_info



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
parser.add_argument('-o', '--output', type=str, help='Output kie json file')
parser.add_argument('-i','--input', type=str, help='Input odt template folder')

args = parser.parse_args()

odt_folder = args.input

json_info = {
    'classes': KEY_LIST,
    'samples':[]
}

odt_templates = []

pdf_dict = {}
for filename in os.listdir(odt_folder):
    if not filename.endswith("odt"):
        continue
    odtin_path = os.path.join(odt_folder, filename)
    
    # odt_templates.append(doc)
    print(filename)
    template_name = os.path.basename(filename)

    print("Replace text to odt...")
    for i in tqdm(range(args.samplenum)):
        doc = opendocument.load(odtin_path)
        replace_dict = gen_info(KEY_LIST)
        # print(replace_dict)
        for key in replace_dict:
            replace_text(doc.topnode, f"$({key})", replace_dict[key])
        doc.save(os.path.join(temp_folder, f"{template_name}_{i}.odt"))    
        pdf_dict[f"{template_name}_{i}.pdf"] = copy.deepcopy(replace_dict)

    print("Odt to pdf...")
    for i in tqdm(range(args.samplenum)):
        # Convert ODT to PDF using unoconv
        # subprocess.run(['unoconv', '-f', 'pdf', '-o', pdf_path, odtout_path])
        subprocess.run(['unoconv', '--format=pdf', '-o', os.path.join(temp_folder, f"{template_name}_{i}.pdf"), 
                                                         os.path.join(temp_folder, f"{template_name}_{i}.odt")])

print("Pdf to KIE...")
for pdf_name in tqdm(pdf_dict):

    pdf_doc = fitz.open(os.path.join(temp_folder,pdf_name))
    replace_dict = pdf_dict[pdf_name]
    for page in pdf_doc:
        pixmap = page.get_pixmap()
        image = bytes2pillow(pixmap.tobytes())
        w, h = image.size
        texts, polygons, lines, line_word_mapping = page_extraction(page, extract_type = "word_KIE")

        links = []
        for line_id in line_word_mapping:
            text_ids = line_word_mapping[line_id]
            for i in range(len(text_ids)-1):
                links.append([text_ids[i], text_ids[i+1]])

        kie_dict = kie_gen(texts = texts, 
                        key_list = KEY_LIST, 
                        replace_dict = replace_dict,
                        lines = lines,
                        line_word_mapping = line_word_mapping)
        sample = {
            "texts": texts,
            "boxes": polygons,
            "links": links,
            "classes": kie_dict,
            "image_width": w,
            "image_height": h,
            "image_base64": pillow2base64(image)
        }
        json_info['samples'].append(sample)

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(json_info, f, ensure_ascii=False)