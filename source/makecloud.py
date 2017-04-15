import tkinter.filedialog
import tkinter.messagebox as messagebox
import zipfile
import collections
import math

import wordcloud
from openpyxl import *

import main

symbols = None
num_ratio_zero = None
quartile1 = None
median = None
quartile3 = None
quartiles = collections.OrderedDict([('red', "hsl(0, 80%, 50%)"),
                                     ('yellow', "hsl(58, 80%, 60%)"),
                                     ('green', "hsl(126, 80%, 60%)"),
                                     ('blue', "hsl(206, 100%, 50%)")])


def generate_word_cloud():
    """Creates a wordcloud showing the most optimal genes to study (low ratio,
     high count) large and in red."""
    global symbols, num_ratio_zero, quartile1, median, quartile3
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

    # output will change header to 'Gene title'
    # will not be compatible with old output
    if 'Gene title' in headers:  # GEO format
        symbol_col = headers.index('Gene symbol')
    else:
        showinfo(title="Incorrect Output Format",
                 message="No 'Gene title' column found. Please rerun process "
                         "to generate an updated output spreadsheet.")
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

        if type(row[symbol_col]) == str and row[total_count_index] > 0 and \
                row[symbol_col] not in [symbol[0] for symbol in symbols]:
            # does not repeat ^
            # took out: row[count_ratio_index] > 0

            # excludes the datetime rows
            # creates a list of tuples (symbol, total count, ratio)
            symbols.append((row[symbol_col], int(row[total_count_index]),
                            row[count_ratio_index]))

    symbols.sort(key=lambda x: x[2])

    # number of symbols with 0 count ratio- will be excluded from quartiles
    num_ratio_zero = len([symbol for symbol in symbols if symbol[2] == 0])

    cloud_width = len(symbols) * 2 if len(symbols) > 200 else 400
    cloud_height = len(symbols) if len(symbols) > 200 else 200
    cloud = wordcloud.WordCloud(max_words=int(len(symbols) / 2),
                                max_font_size=100, width=cloud_width,
                                height=cloud_height)

    # nothing actually wrong with this vvv
    cloud.generate_from_frequencies(tuple([symbol[:2] for symbol in symbols]))

    quarter_size = math.floor((len(symbols) - num_ratio_zero) / 4)
    quartile1 = num_ratio_zero + quarter_size
    median = num_ratio_zero + quarter_size * 2
    quartile3 = num_ratio_zero + quarter_size * 3

    cloud.recolor(color_func=set_color_scale)
    output_file = file[:-5] + '_wordcloud.png'
    cloud.to_file(output_file)
    return output_file


# recolors the word cloud based on the quartiles sorted by ratio size
def set_color_scale(word, font_size, position, orientation, font_path,
                    random_state=None):
    symbol_index = [symbol[0] for symbol in symbols].index(word)
    if symbol_index < quartile1:
        return quartiles['red']  # red
    elif symbol_index < median:
        return quartiles['yellow']  # yellow
    elif symbol_index < quartile3:
        return quartiles['green']  # green
    else:
        return quartiles['blue']  # blue
        # if other symbols get returned that aren't red, yellow, green or blue
        # they were not added to the symbol chart and processed through this
        # function (which they should have been)

