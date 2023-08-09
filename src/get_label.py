import json
from PIL import Image
from .image_convert import pillow2base64
import os
from pprint import pprint
import base64

def rec_to_polygon(box):
    x1 = box[0]
    y1 = box[1]
    x2 = box[2]
    y2 = box[3]
    return [[float(x1), float(y1)], [float(x2), float(y1)], [float(x2), float(y2)], [float(x1), float(y2)]]

def polygon_to_rectangle(polygon):
    x1= min([point[0] for point in polygon])
    x2= max([point[0] for point in polygon])
    y1= min([point[1] for point in polygon])
    y2= max([point[1] for point in polygon])

    return [[x1, y1], [x2, y2]]

def labelme_gen(polygons: dict, image: Image, filename: str, savefolder: str, box_type = "polygon"):
    """
    Generate a LabelMe annotation file (.json) for the given polygons and image.

    Args:
        polygons (list): dict of List of polygon points representing the shapes.
        image (PIL.Image): Input image.
        filename (str): Name of the file (without extension) to be saved.
        savefolder (str): Path to the folder where the generated files will be saved.

    Returns:
        None
    """
    shapes = []
    for label in polygons:
        for point in polygons[label]:
            polygon = [[float(x[0]), float(x[1])] for x in point] if isinstance(point[0], list) else rec_to_polygon(point)
            if box_type == "polygon":
                shapes.append({
                    'label' : label, 
                    'points' : polygon, # point, 
                    'group_id': None,
                    'shape_type': 'polygon',
                    'flags': {}
                })
            else:
                rectangle = polygon_to_rectangle(polygon)
                shapes.append({
                    'label' : label, 
                    'points' : rectangle, # point, 
                    'group_id': None,
                    'shape_type': 'rectangle',
                    'flags': {}
                })
            
    w, h = image.size
    image.save(os.path.join(savefolder, f"{filename}.jpg"))

    # with open(os.path.join(savefolder, f"{filename}.jpg"), "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read()).decode("utf-8")


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
            line_word_mapping: dict = None) -> dict:
    """
    Generate a dictionary mapping text IDs to class IDs using the provided texts and key information.

    Args:
        texts (list): List of texts to be mapped.
        key_list (list): List of class names.
        replace_dict (dict): Dictionary mapping class names to class strings.
        lines (list, optional): List of lines corresponding to the texts (default: None).
        line_word_mapping (dict, optional): Dictionary mapping line IDs to word IDs (default: None).

    Returns:
        dict: A dictionary mapping text IDs to class IDs.

    Note:
        This function is not yet completed. If a label has more than or equal to two lines, 
        the class will be incorrectly assigned to a line other than the first line, 
        whereas the expectation is to label it to the first line.
        Example : "seller_address"
    """

    kie = {}
    if lines is None:
        for class_id, class_name in enumerate(key_list):
            class_string = replace_dict[class_name]
            for text_id, text in enumerate(texts):
                if text in class_string or class_string in text:
                    # print("class_name: ",class_name)
                    # print("class_string: ",class_string)
                    # print("text: ",text)
                    # print('='*10)
                    kie[f'{text_id}'] = class_id
        return kie, []
    else:
        class_last_box = {}
        line_links = []
        for class_id, class_name in enumerate(key_list):
            class_string = replace_dict[class_name]
            for line_id, line in enumerate(lines):
                if line in class_string or class_string in line:
                    text_id = line_word_mapping[str(line_id)][0]
                    if class_id not in class_last_box:
                        class_last_box[class_id] = [line_word_mapping[str(line_id)][-1], line_id]
                        kie[f'{text_id}'] = class_id
                    elif  abs(class_last_box[class_id][1] - line_id) >4:
                        class_last_box[class_id] = [line_word_mapping[str(line_id)][-1], line_id]
                        kie[f'{text_id}'] = class_id
                    else:
                        line_links.append([class_last_box[class_id][0], text_id])
                        class_last_box[class_id] = [line_word_mapping[str(line_id)][-1], line_id]
        # line_links = []
        return kie, line_links