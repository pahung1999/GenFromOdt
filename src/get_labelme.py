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