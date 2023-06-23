import fitz
import numpy as np

def page_extraction_word(page):
    texts = []
    polygons = []
    for x1, y1, x2, y2, word, a, b, c in page.get_text("words"):
        texts.append(word)
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    
    return texts, polygons

def page_extraction_block(page):
    texts = []
    polygons = []
    for x1, y1, x2, y2, block, a, b in page.get_text("blocks"):
        if b != 0:
            continue
        texts.append(block[:-1])
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    
    return texts, polygons

def merge_rectangles(rectangles):
    # Find the minimum and maximum x and y coordinates of all rectangles
    x1_values = [rect[0] for rect in rectangles]
    y1_values = [rect[1] for rect in rectangles]
    x2_values = [rect[2] for rect in rectangles]
    y2_values = [rect[3] for rect in rectangles]
    
    min_x = min(x1_values)
    min_y = np.mean(y1_values)

    max_x = max(x2_values)
    max_y = np.mean(y2_values)
    # max_x = max([x + w for x, w in zip(x_values, widths)])
    # max_y = max([y + h for y, h in zip(y_values, heights)])
    
    return [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]


def page_extraction_line(page):
    text_info = {}
    for x1, y1, x2, y2, word, a, b, c in page.get_text("words"):
        line_id = f"{a}_{b}"
        if line_id not in text_info:
            text_info[line_id] = {
                'text' : [word],
                'rectangle': [[x1, y1, x2, y2]]
            }
        else:
            text_info[line_id]['text'].append(word)
            text_info[line_id]['rectangle'].append([x1, y1, x2, y2])

    texts = []
    polygons = []

    for key in text_info:
        text = ' '.join(text_info[key]['text'])
        texts.append(text)
        polygon = merge_rectangles(text_info[key]['rectangle'])
        polygons.append(polygon)
        # texts.append(word)
        # polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    return texts, polygons

def page_extraction(page, extract_type = "word"):
    type_list = ['word', 'block', 'line']
    if extract_type not in type_list:
        print("No type in type_list")
    if extract_type == "word":
        return page_extraction_word(page)
    if extract_type == "block":
        return page_extraction_block(page)
    if extract_type == "line":
        return page_extraction_line(page)