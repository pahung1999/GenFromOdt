import json
from PIL import Image
from .image_convert import pillow2base64
import os

def labelme_gen(polygons: list, image: Image, filename: str, savefolder: str):

    shapes = []
    for point in polygons:
        shapes.append({
            'label' : 'text', 
            'points' : point, 
            'group_id': None,
            'shape_type': 'polygon',
            'flags': {}
        })
    
    w, h = image.size
    image.save(os.path.join(savefolder, f"{filename}.jpg"))
    labelme_data = {
        'version': '5.1.1',
        'flags': {}, 
        'shapes': shapes, 
        'imagePath' : f'{filename}.jpg', 
        'imageData': pillow2base64(image),
        'imageHeight': h, 
        'imageWidth': w
    }

    json_out = os.path.join(savefolder, f"{filename}.json")
    with open(json_out, "w") as out:
        json.dump(labelme_data, out)
    return


def kie_gen(texts: list, 
            key_list: list, 
            replace_dict: dict,
            lines: list = None,
            line_word_mapping : dict = None,
            ):
    kie = {}
    if lines is None:
        for class_id, class_name in enumerate(key_list):
            if class_name == "seller_address":
                continue
            class_string = replace_dict[class_name]
            for text_id, text in enumerate(texts):
                if text in class_string or class_string in text:
                    # print("class_name: ",class_name)
                    # print("class_string: ",class_string)
                    # print("text: ",text)
                    # print('='*10)
                    kie[f'{text_id}'] = class_id
        return kie
    else:
        for class_id, class_name in enumerate(key_list):
            if class_name == "seller_address":
                continue
            class_string = replace_dict[class_name]
            for line_id, line in enumerate(lines):
                if line in class_string or class_string in line:
                    text_id = line_word_mapping[str(line_id)][0]
                    kie[f'{text_id}'] = class_id
        return kie