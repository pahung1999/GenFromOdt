import json
from PIL import Image
from .image_convert import pillow2base64
import os

def labelme_gen(polygons: list, image: Image, filename: str, savefolder: str):
    """
    Generate a LabelMe annotation file (.json) for the given polygons and image.

    Args:
        polygons (list): List of polygon points representing the shapes.
        image (PIL.Image): Input image.
        filename (str): Name of the file (without extension) to be saved.
        savefolder (str): Path to the folder where the generated files will be saved.

    Returns:
        None
    """
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

    Error:
        This function is not yet completed. If a label has more than or equal to two lines, 
        the class will be incorrectly assigned to a line other than the first line, 
        whereas the expectation is to label it to the first line.
        Example : "seller_address"
    """

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