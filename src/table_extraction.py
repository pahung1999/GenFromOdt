import numpy as np


def check_same_length(list_of_lists):
    length = len(list_of_lists[0])
    return all(len(lst) == length for lst in list_of_lists[1:])

def merge_boxes(box_list):
    # Convert the list to a NumPy array
    box_array = np.array(box_list)

    # Calculate the minimum and maximum values
    min_x1 = np.min(box_array[:, 0])
    max_x2 = np.max(box_array[:, 2])
    min_y1 = np.min(box_array[:, 1])
    max_y2 = np.max(box_array[:, 3])

    return [min_x1, min_y1, max_x2, max_y2]

def extract_table(table, h):
    lines = table.cells
    rows = []
    cells = []
    for i, boxes in enumerate(lines):
        new_line = []
        # print(len(cell))
        for j, box in enumerate(boxes):
            true_box = [int(box.x1), int(h-box.y2) , int(box.x2), int(h-box.y1)]
            new_line.append(true_box)
            cells.append(true_box)
            # break
        rows.append(new_line)

    
    if check_same_length(rows):
        columns = [[] for i in range(len(rows[0]))]
        for row in rows:
            for i, cell in enumerate(row):
                columns[i].append(cell)
    else:
        columns = []

    return {
        "row" : [(merge_boxes(row)) for row in rows],
        "cell" : cells,
        "table" : [merge_boxes(cells)],
        "column" : [merge_boxes(column) for column in columns],
    }

def column_from_text(col_polygons, text_polygons):
    column_text_map = [[] for i in range(len(col_polygons))]
    text_cens = [[sum(p[0] for p in poly)/4, sum(p[1] for p in poly)/4] for poly in text_polygons]

    if isinstance(col_polygons[0][0], list):
        for i, cols in enumerate(col_polygons):

            col_x_min = min([p[0] for p in cols])  
            col_x_max = max([p[0] for p in cols]) 
            col_y_min = min([p[1] for p in cols]) 
            col_y_max = max([p[1] for p in cols])   

            for j, cen_point in enumerate(text_cens):
                if cen_point[0] > col_x_min and cen_point[0] < col_x_max and cen_point[1] > col_y_min and cen_point[1] < col_y_max:
                    column_text_map[i].append(j)
    else:
        for i, cols in enumerate(col_polygons):

            col_x_min = cols[0]
            col_x_max = cols[2]
            col_y_min = cols[1]
            col_y_max = cols[3]

            for j, cen_point in enumerate(text_cens):
                if cen_point[0] > col_x_min and cen_point[0] < col_x_max and cen_point[1] > col_y_min and cen_point[1] < col_y_max:
                    column_text_map[i].append(j)

    new_cols_list = []
    for text_id_list in column_text_map:
        min_x = min([min([p[0] for p in text_polygons[text_id]]) for text_id in text_id_list])
        max_x = max([max([p[0] for p in text_polygons[text_id]]) for text_id in text_id_list])
        min_y = min([min([p[1] for p in text_polygons[text_id]]) for text_id in text_id_list])
        max_y = max([max([p[1] for p in text_polygons[text_id]]) for text_id in text_id_list])
        new_cols_list.append([min_x, min_y, max_x, max_y])
        
    return new_cols_list

def two_boxes_in_row(table1, table2, max_error = 10, box_type = 'table'):
    cen1 = [(table1[2]+table1[0])/2, (table1[3]+table1[1])/2]
    cen2 = [(table2[2]+table2[0])/2, (table2[3]+table2[1])/2]
    distance_x = abs(cen1[0] - cen2[0])
    distance_y = abs(cen1[1] - cen2[1])
    w1, h1 = abs(table1[2] - table1[0]), abs(table1[3] - table1[1])
    w2, h2 = abs(table2[2] - table2[0]), abs(table2[3] - table2[1])
    
    #Check if same column
    if box_type != 'row': 
        if abs(table1[0]-table2[0]) <= max_error and abs(table1[2]-table2[2]) <= max_error and abs(h1 + h2 - 2*distance_y) <= max_error:
            return True

    #Check if same row
    if box_type != 'column': 
        if abs(table1[1]-table2[1]) <= max_error and abs(table1[3]-table2[3]) <= max_error and abs(w1 + w2 - 2*distance_x) <= max_error:
            return True

    return False


def merge_table_element(tables_list, max_error = 10, box_type = 'table'):
    
    merge_flag = True
    while merge_flag:
        merge_flag = False
        for i, table1 in enumerate(tables_list):
            for j, table2 in enumerate(tables_list):
                if i == j:
                    continue
                if two_boxes_in_row(table1, table2, max_error = max_error, box_type = box_type):
                    tables_list[i] = merge_boxes([table1, table2])
                    del tables_list[j]
                    merge_flag = True
                    break
            if merge_flag == True:
                break
    return tables_list