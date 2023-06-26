import fitz
import numpy as np

def page_extraction_word(page):
    #Extract words
    texts = []
    polygons = []
    for x1, y1, x2, y2, word, block_id, line_id, text_id in page.get_text("words"):
        texts.append(word)
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    
    return texts, polygons

def page_extraction_block(page):
    #Extract paragraphs 
    texts = []
    polygons = []
    for x1, y1, x2, y2, block, block_id, block_type in page.get_text("blocks"):
        if block_type != 0:
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
    #Extract lines
    text_info = {}
    for x1, y1, x2, y2, word, block_id, line_id, text_id in page.get_text("words"):
        line_id = f"{block_id}_{line_id}"
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


def page_extraction_word_KIE(page):
    #Extract words and line mapping
    texts = []
    polygons = []
    lines = []
    #Map of line and first word of line (for KIE label)
    line_word_mapping = {}

    #Extract lines
    text_info = {}
    for x1, y1, x2, y2, word, block_id, line_id, text_id in page.get_text("words"):
        texts.append(word)
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])

        line_id = f"{block_id}_{line_id}"
        if line_id not in text_info:
            text_info[line_id] = {
                'text' : [word],
                'text_id': [len(texts)-1]
            }
        else:
            text_info[line_id]['text'].append(word)
            text_info[line_id]['text_id'].append(len(texts)-1)

    for key in text_info:
        text = ' '.join(text_info[key]['text'])
        lines.append(text)
        line_word_mapping[str(len(lines)-1)] = text_info[key]['text_id']
    
    return texts, polygons, lines, line_word_mapping

def page_extraction(page, extract_type = "word"):
    type_list = ['word', 'word_KIE', 'block', 'line']
    if extract_type not in type_list:
        print("No type in type_list")
    if extract_type == "word":
        return page_extraction_word(page)
    if extract_type == "word_KIE":
        return page_extraction_word_KIE(page)
    if extract_type == "block":
        return page_extraction_block(page)
    if extract_type == "line":
        return page_extraction_line(page)