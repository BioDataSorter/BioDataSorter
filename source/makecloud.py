import tkinter.filedialog
import tkinter.messagebox as messagebox
import zipfile
from collections import OrderedDict

import wordcloud
from openpyxl import *

import main

symbols = None


def generate_word_cloud():
    """Creates a wordcloud showing the most optimal genes to study (low ratio,
     high count) large and in red."""
    global symbols
    _filename = main.form_elements['filename']
    initial_dir = _filename[:_filename.rfind('/')] \
        if _filename is not None else None
    initial_file = _filename.split('/')[-1] if _filename is not None else None
    options = {
        'defaultextension': '.xlsx',
        'filetypes': [('excel files', '.xlsx')],
        'initialdir': initial_dir,
        'title': "Choose an output file",
        'initialfile': initial_file
    }
    file = tkinter.filedialog.askopenfilename(**options)
    try:
        wb = load_workbook(filename=file, data_only=True)
    except (FileNotFoundError, zipfile.BadZipfile):
        return
    ws = wb.active
    rows = main.read_sheet(ws)
    headers = rows[0]
    run_again_msg = " Run the program to generate a correctly formatted "\
                    "output correctly formatted output file to graph."
    showinfo = messagebox.showinfo
    if 'SYMBOL' in headers:  # Winthrop format
        symbol_col = headers.index('SYMBOL')
    elif 'Gene title' in headers:  # GEO format
        symbol_col = headers.index('Gene symbol')
    else:
        showinfo(title="Incorrect Output Format",
                 message="No 'SYMBOL' column or 'Gene title' "
                         "column found.")
        return
    if 'TOTAL COUNT' in headers:
        total_count_index = headers.index('TOTAL COUNT')
    else:
        showinfo(title="Incorrect Output Format",
                 message="No 'TOTAL COUNT' column found." + run_again_msg)
        return
    if 'COUNT RATIO' in headers:
        count_ratio_index = headers.index('COUNT RATIO')
    else:
        showinfo(title="Incorrect Output Format",
                 message="No 'COUNT RATIO' column found." + run_again_msg)
        return

    symbols = []
    for row in rows[1:]:
        if row[symbol_col] is None or row[total_count_index] is None or \
                        row[count_ratio_index] is None:
            showinfo(title="Incorrect Output Format",
                     message="Empty cells in mandatory columns." +
                             run_again_msg)
            return

        # TODO cut off for total count for 0 ratio: 100 citations?
        if type(row[symbol_col]) == str and row[total_count_index] > 0 and \
                row[count_ratio_index] > 0 and \
                row[symbol_col] not in [symbol[0] for symbol in symbols]:

            # excludes the datetime rows
            # creates a list of tuples (symbol, total count, ratio)
            symbols.append((row[symbol_col], int(row[total_count_index]),
                            row[count_ratio_index]))
    symbols.sort(key=lambda x: x[2])

    cloud_width = len(symbols) * 2 if len(symbols) > 200 else 400
    cloud_height = len(symbols) if len(symbols) > 200 else 200
    cloud = wordcloud.WordCloud(max_words=int(len(symbols) / 2),
                                max_font_size=100, width=cloud_width,
                                height=cloud_height)

    # nothing actually wrong with this
    cloud.generate_from_frequencies(tuple([symbol[:2] for symbol in symbols]))
    cloud.recolor(color_func=set_color_scale)
    output_file = file[:-5] + '_wordcloud.png'
    cloud.to_file(output_file)
    return output_file


def set_color_scale(word, font_size, position, orientation, font_path,
                    random_state=None):
    quartile1 = round(len(symbols) / 4)
    median = quartile1 * 2
    quartile3 = quartile1 * 3
    symbol_index = [symbol[0] for symbol in symbols].index(word)
    if symbol_index < quartile1:
        return "hsl(0, 80%, 50%)"
    elif symbol_index < median:
        return "hsl(58, 80%, 60%)"
    elif symbol_index < quartile3:
        return "hsl(126, 80%, 60%)"
    else:
        return "hsl(206, 100%, 50%)"
        # if other symbols get returned that aren't red, yellow, green or blue
        # they were not added to the symbol chart and processed through this
        # function

    # symbol_ratio = symbols[[symbol[0] for symbol in symbols].index(word)][2]
    # ratio_to_color = (
    #     (0.01, "hsl(0, 80%, 50%)"),  # red
    #     (0.05, "hsl(58, 80%, 60%)"),  # yellow
    #     (0.1, "hsl(126, 80%, 60%)")  # green
    # )
    # ratio_to_color = OrderedDict(ratio_to_color)
    # for ratio_min in ratio_to_color:
    #     if symbol_ratio < ratio_min:
    #         return ratio_to_color[ratio_min]
