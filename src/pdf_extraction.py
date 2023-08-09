import fitz
import numpy as np

def spiltpage_pdf(pdf_path):
    name, ext = os.path.splitext(pdf_path)
    pdf_reader = PdfFileReader(pdf_path)
    numPages = pdf_reader.numPages
    for page_number in range(numPages):
        output_pdf_path = f"{name}_{page_number}.pdf"
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(page_number))
        
        with open(output_pdf_path, "wb") as output_pdf:
            pdf_writer.write(output_pdf)
    return numPages
    
def page_extraction_word(page):
    """
    Extract individual words and their corresponding polygons from a page.

    Args:
        page (fitz.Page): The page to extract words from.

    Returns:
        tuple: A tuple containing the extracted words and their polygons.
            texts (list): A list of words extracted from the page.
            polygons (list): A list of polygons corresponding to each word.
    """
    texts = []
    polygons = []
    for x1, y1, x2, y2, word, block_id, line_id, text_id in page.get_text("words"):
        texts.append(word)
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    
    return texts, polygons

def page_extraction_block(page):
    """
    Extract paragraphs (blocks) and their corresponding polygons from a page.

    Args:
        page (fitz.Page): The page to extract blocks from.

    Returns:
        tuple: A tuple containing the extracted blocks and their polygons.
            texts (list): A list of blocks (paragraphs) extracted from the page.
            polygons (list): A list of polygons corresponding to each block.
    """
    texts = []
    polygons = []
    for x1, y1, x2, y2, block, block_id, block_type in page.get_text("blocks"):
        if block_type != 0:
            continue
        texts.append(block[:-1])
        polygons.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    
    return texts, polygons

def merge_rectangles(rectangles):
    """
    Merge multiple rectangles into a single bounding rectangle.

    Args:
        rectangles (list): A list of rectangles to merge.

    Returns:
        list: The merged bounding rectangle represented as a list of coordinates.
    """
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
    """
    Extract lines of text and their corresponding polygons from a page.

    Args:
        page (fitz.Page): The page to extract lines from.

    Returns:
        tuple: A tuple containing the extracted lines and their polygons.
            texts (list): A list of lines extracted from the page.
            polygons (list): A list of polygons corresponding to each line.
    """

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
    """
    Extract words, polygons, lines, and line-word mappings from a page.

    Args:
        page (fitz.Page): The page to extract information from.

    Returns:
        tuple: A tuple containing the extracted words, polygons, lines, and line-word mappings.
            texts (list): A list of words extracted from the page.
            polygons (list): A list of polygons corresponding to each word.
            lines (list): A list of lines extracted from the page.
            line_word_mapping (dict): A dictionary mapping line IDs to word IDs.
    """
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
    """
    Extract information from a page based on the specified extraction type.

    Args:
        page (fitz.Page): The page to extract information from.
        extract_type (str): The type of extraction to perform. Possible values: 'word', 'word_KIE', 'block', 'line'.

    Returns:
        tuple: A tuple containing the extracted information based on the extraction type.
            texts (list): A list of extracted text elements.
            polygons (list): A list of polygons corresponding to each text element.
            lines (list): A list of extracted lines.
            line_word_mapping (dict): A dictionary mapping line IDs to word IDs.
    """
    type_list = ['word', 'block', 'line']
    if extract_type not in type_list:
        print("No type in type_list")
    if extract_type == "word":
        return page_extraction_word(page)
    if extract_type == "block":
        return page_extraction_block(page)
    if extract_type == "line":
        return page_extraction_line(page)