from odf import text, teletype


def replace_text_single(Elem, item, pattern, repl):
    s = teletype.extractText(item)
    if s.find(pattern) != -1:
        # repl = get_format(pattern)(repl)
        s = s.replace(pattern, repl)
        new_item = Elem()
        new_item.setAttribute('stylename', item.getAttribute('stylename'))
        new_item.addText(s)
        item.parentNode.insertBefore(new_item, item)
        try:
            # Sometime, the text is replaced in the parent node
            # But not updated in the child node
            item.parentNode.removeChild(item)
        except Exception:
            # print_exc()
            print(
                f"Fail to delete child node when replace {pattern} -> {repl}")
        return new_item
    else:
        return item

def replace_text(node, k, v):
    elements = [text.H, text.P, text.Span]
    for Elem in elements:
        for elem in node.getElementsByType(Elem):
            if k in str(elem):
                elem = replace_text_single(Elem, elem, k, str(v))
    return node