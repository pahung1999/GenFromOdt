import yaml
import json
import os
import fitz
from odf import opendocument
from src.odt_convert import replace_text, gen_info
from src.image_convert import bytes2pillow
from src.pdf_extraction import page_extraction_word_KIE
from src.image_convert import bytes2pillow, pillow2base64
from src.get_label import kie_gen
from tqdm import tqdm
import subprocess

yaml_path = "./config/kie.yml"
with open(yaml_path, 'r') as file:
    config_gen = yaml.safe_load(file)

key_dict = config_gen['key_dict_path']
with open(key_dict, "r", encoding="utf-8") as f:
    key_dict=json.load(f)

def mix_label_list(label_list):
    new_label = []
    for labels in label_list:
        for label in labels:
            if label not in new_label:
                new_label.append(label)
    return new_label

key_type_list = []
for key_type in config_gen["key_and_odt"]:
    if key_type not in key_dict:
        raise Exception(f"{key_type} not in key_dict")
    else:
        key_type_list.append(key_type)

if config_gen['label'] is None:
    label_list = [key_dict[x]['label'] for x in key_type_list]
    labels = mix_label_list(label_list)
else:
    labels = config_gen['label']

print("output labels: ", labels)


json_info = {
    'classes': labels,
    'samples':[]
}


for key_type in key_type_list:
    
    #key to replace in odt file
    replace_key = key_dict[key_type]['replace_key']
    
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
                replace_text(doc.topnode, f"$({key})", replace_dict[key])
            doc.save("temp.odt")

            #Save to pdf
            subprocess.run(['unoconv', '--format=pdf', '-o', "./temp.pdf", "./temp.odt"])

            pdf_doc = fitz.open("temp.pdf")
            for j, page in enumerate(pdf_doc):
                pixmap = page.get_pixmap()
                image = bytes2pillow(pixmap.tobytes())
                w, h = image.size
                shape_dict = {}

                texts, polygons, lines, line_word_mapping = page_extraction_word_KIE(page)

                links = []
                for line_id in line_word_mapping:
                    text_ids = line_word_mapping[line_id]
                    # if str(text_ids[0]) not in kie_dict:
                    #     continue 
                    for i in range(len(text_ids)-1):
                        links.append([text_ids[i], text_ids[i+1]])

                if config_gen['box_label'] == "line":
                    kie_dict, line_links = kie_gen(texts = lines, 
                                    key_list = labels, 
                                    replace_dict = replace_dict,
                                    lines = None,
                                    line_word_mapping = None)
                                    
                if config_gen['box_label'] == "word": 
                    kie_dict, line_links = kie_gen(texts = texts, 
                                key_list = labels, 
                                replace_dict = replace_dict,
                                lines = lines,
                                line_word_mapping = line_word_mapping)

                for connect in line_links:
                    links.append(connect)

                max_label = 0
                for labelkey in kie_dict:
                    if int(labelkey) > max_label:
                        max_label = int(labelkey)
                #     label = labels[kie_dict[labelkey]]
                #     text = lines[int(labelkey)]
                #     print(f"{label}: {text}")
                # print("="*10)
                # print(f"{max_label}, {len(lines)}")

                sample = {
                    "texts": texts if config_gen['box_label'] == "word" else lines,
                    "boxes": polygons,
                    "links": links if config_gen['box_label'] == "word" else [],
                    "classes": kie_dict if config_gen['pre_label'] else {},
                    "image_width": w,
                    "image_height": h,
                    "image_base64": pillow2base64(image)
                }
                json_info['samples'].append(sample)

print("Saving...")
with open(config_gen['output_path'], "w", encoding="utf-8") as f:
    json.dump(json_info, f, ensure_ascii=False)