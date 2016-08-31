import tkinter.filedialog
import tkinter.messagebox
import zipfile
from collections import OrderedDict

import wordcloud
from openpyxl import *

import main

symbols = None


def generate_word_cloud():
    """Creates a wordcloud showing the most optimal genes to study (low ratio , high count) large and in red."""
    global symbols
    initial_dir = main.filename[:main.filename.rfind('/')] if main.filename is not None else None
    initial_file = main.filename.split('/')[-1] if main.filename is not None else None
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
    if 'SYMBOL' in headers:  # Winthrop format
        symbol_col = headers.index('SYMBOL')
    elif 'Gene title' in headers:  # GEO format
        symbol_col = headers.index('Gene title')
    else:
        tkinter.messagebox.showinfo(title="Incorrect Output Format",
                                    message="No 'SYMBOL' column or 'Gene title' column found.")
        return
    if 'TOTAL COUNT' in headers:
        total_count_index = headers.index('TOTAL COUNT')
    else:
        tkinter.messagebox.showinfo(title="Incorrect Output Format",
                                    message="No 'TOTAL COUNT' column found. Run the program to generate a " +
                                            "correctly formatted output file to graph.")
        return
    if 'COUNT RATIO' in headers:
        count_ratio_index = headers.index('COUNT RATIO')
    else:
        tkinter.messagebox.showinfo(title="Incorrect Output Format",
                                    message="No 'COUNT RATIO' column found. Run the program to generate a " +
                                            "correctly formatted output file to graph.")
        return

    symbols = []
    for row in rows[1:]:
        if row[symbol_col] is None or row[total_count_index] is None or row[count_ratio_index] is None:
            tkinter.messagebox.showinfo(title="Incorrect Output Format",
                                        message="Empty cells in mandatory columns. Run the program to generate a " +
                                        "correctly formatted output file to graph.")
            return
        if type(row[symbol_col]) == str and row[total_count_index] > 0 and \
                row[symbol_col] not in [symbol[0] for symbol in symbols]:  # excludes the datetime rows
            symbols.append((row[symbol_col], int(row[total_count_index]), row[count_ratio_index]))

    cloud_width = len(symbols) * 2 if len(symbols) > 200 else 400
    cloud_height = len(symbols) if len(symbols) > 200 else 200
    cloud = wordcloud.WordCloud(max_words=int(len(symbols) / 2), max_font_size=100, width=cloud_width,
                                height=cloud_height)

    cloud.generate_from_frequencies(tuple([symbol[:2] for symbol in symbols]))  # nothing actually wrong with this
    cloud.recolor(color_func=set_color_scale)
    output_file = file[:-5] + '_wordcloud.png'
    cloud.to_file(output_file)
    return output_file


def set_color_scale(word, font_size, position, orientation, font_path, random_state=None):
    symbol_ratio = symbols[[symbol[0] for symbol in symbols].index(word)][2]
    ratio_to_color = (
        (0.01, "hsl(0, 80%, 50%)"),  # red
        (0.05, "hsl(58, 80%, 60%)"),  # yellow
        (0.1, "hsl(126, 80%, 60%)")  # green
    )
    ratio_to_color = OrderedDict(ratio_to_color)
    for ratio_min in ratio_to_color:
        if symbol_ratio < ratio_min:
            return ratio_to_color[ratio_min]
