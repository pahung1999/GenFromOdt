# import argparse

# from odf.style import PageLayout, PageLayoutProperties
# import copy
# import random

import yaml
import json
import os
import fitz
from odf import opendocument
from src.odt_convert import replace_text, gen_info
from src.image_convert import bytes2pillow
from src.pdf_extraction import page_extraction
from src.get_label import labelme_gen
from src.table_extraction import extract_table
from tqdm import tqdm
import subprocess
import camelot


yaml_path = "./config/labelme.yml"
with open(yaml_path, 'r') as file:
    config_gen = yaml.safe_load(file)

key_dict = config_gen['key_dict_path']
with open(key_dict, "r", encoding="utf-8") as f:
    key_dict=json.load(f)


for key_type in config_gen["key_and_odt"]:
    
    if key_type not in key_dict:
        raise Exception(f"{key_type} not in key_dict")
    else:
        #key to replace in odt file
        replace_key = key_dict[key_type]['replace_key']

        #label name to save to kie json file
        label_list = key_dict[key_type]['label']

    
    for odt_file in os.listdir(config_gen['odt_dir']):
        odt_temp_name = os.path.splitext(odt_file)[0]
        if odt_temp_name not in config_gen["key_and_odt"][key_type]:
            continue

        print(f"Gen {key_type} from {odt_file}")
        
        for i in tqdm(range(config_gen["sample_num"])):

            doc = opendocument.load(os.path.join(config_gen['odt_dir'], odt_file))
            #Gen replace dict
            replace_dict =  gen_info(key_type, replace_key) 
            
            #Replace odt file
            for key in replace_dict:
                # print("type: ", type(replace_dict[key]))
                # print("replace_dict[key]: ", replace_dict[key])
                replace_text(doc.topnode, f"$({key})", replace_dict[key])
            doc.save("temp.odt")

            #Save to pdf
            subprocess.run(['unoconv', '--format=pdf', '-o', "temp.pdf", "temp.odt"])

            pdf_doc = fitz.open("temp.pdf")
            tables = camelot.read_pdf("temp.pdf", flavor = "lattice", pages='all')
            for j, page in enumerate(pdf_doc):
                pixmap = page.get_pixmap()
                image = bytes2pillow(pixmap.tobytes())
                w, h = image.size

                shape_dict = extract_table(tables[j], h)

                # for box_label in config_gen['box_label']:
                #     texts, polygons = page_extraction(page, extract_type = box_label)
                #     shape_dict[box_label] = polygons

                labelme_gen(shape_dict, 
                            image, 
                            f'{odt_temp_name}_{i:04d}_page_{j:02d}', 
                            config_gen['output_dir'])
    

