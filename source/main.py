#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
This program sends gene symbols to the PubMed database to retrieve the number of citations.

This is a project that we are working on for Winthrop University Hospital for genes to study
in diabetes and multiple sclerosis. The program takes data in the form of Excel spreadsheets
that have a gene 'Symbol' column and 'Synonyms' column, like the spreadsheets that can be
downloaded from NCBI's Gene Expression Omnibus (GEO), which is a public functional genomics
data repository for array-based and sequence-based data.
"""

import datetime
import os
import socket
import threading
import time
import tkinter.filedialog
import tkinter.messagebox
from tkinter import *
from urllib import request
from urllib.error import URLError

import mygene
import requests
from Bio import Entrez
from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.utils import _get_column_letter

import layout

__version__ = "0.0.1"

# =======
# GLOBALS
# =======

wb = None
filename = None  # includes path and name
save_as_name = None
symbol_col_num = None
pb_int = 0  # global variable for num of times get_count has been executed
total_queries = 0
total_count_col = 29
ask_quit = False
ask_save_and_quit = False
num_genes = 0

# this is a global variable so the user input can be saved right after the program is run
form_elements = {
    'filename': filename,
    'email': None,
    'keywords': None,
    'save_as_name': save_as_name,
    'column_letters': None,
    'num_genes': None,
    'descriptions': None,
    'sort': None
}


def get_entries(root):
    global wb, total_queries, total_count_col, num_genes, form_elements

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def internet_on():
        try:
            request.urlopen('http://130.14.29.109', timeout=1)  # tries pubmed.gov ip
            return True
        except (URLError, socket.timeout) as err:
            print(str(err))
            return False

    if not internet_on():
        tkinter.messagebox.showwarning(title='Connect to internet',
                                       message="Make sure you are connected to internet before starting.")
        return

    # set all values to global variable
    form_elements['filename'] = filename
    form_elements['email'] = root.custom_frames['FormPage'].ents['Email'].get()
    keywords_str = root.custom_frames['FormPage'].ents['Keywords'].get()
    form_elements['keywords'] = [x.strip() for x in keywords_str.split(',')] if keywords_str != '' else []

    if filename is None:
        tkinter.messagebox.showinfo(title='Error', message="Please select a file to sort.")
        return

    # the input is turned into a list of keywords
    try:
        wb = try_file(filename)
    except TypeError:
        tkinter.messagebox.showinfo(title='Error', message="Unexpected spreadsheet type.")
        return
    except FileNotFoundError as e:
        tkinter.messagebox.showinfo(title='Error', message=str(e))
    ws = wb.active
    if root.custom_frames['AdvancedPage'].v.get() == 'SELECT':
        if root.custom_frames['AdvancedPage'].entry.get() == '' or not \
                is_number(root.custom_frames['AdvancedPage'].entry.get()):
            tkinter.messagebox.showinfo(title='Invalid input', message='Insert a number for \'Top x genes\'.')
            return
        if int(root.custom_frames['AdvancedPage'].entry.get()) >= ws.max_row:
            num_genes = ws.max_row - 1
        else:
            num_genes = int(root.custom_frames['AdvancedPage'].entry.get())
    else:
        num_genes = ws.max_row - 1
    form_elements['num_genes'] = num_genes
    if root.custom_frames['AdvancedPage'].auto_manual_columns.get() == 'AUTO':
        form_elements['column_letters'] = 'AUTO'
    else:
        form_elements['column_letters'] = [root.custom_frames['AdvancedPage'].symbol_col,
                                           root.custom_frames['AdvancedPage'].synonyms_col]
    form_elements['descriptions'] = root.custom_frames['AdvancedPage'].desc.get() == 1
    form_elements['sort'] = root.custom_frames['AdvancedPage'].sort.get() == 1

    root.custom_frames['AdvancedPage'].b3.config(state="disabled")
    try:
        rows = remove_duplicates(ws)
        rows = rows[:num_genes+1]  # cuts down to the number of genes that the user wants
        total_count_col = ws.max_column  # this is the column that TOTAL COUNT will be written in
        genes = get_aliases(rows)
        num_genes = len(genes)
        print("Num genes: %d" % num_genes)
        total_queries = num_genes * 2
        if root.custom_frames['AdvancedPage'].desc.get() == 1:  # if the box is checked
            total_queries += num_genes  # adds the number of comment queries
        print("Total queries: %d" % total_queries)
        ws = wb.create_sheet(title='Output', index=0)
        write_rows(rows, ws)

        try:
            root.custom_frames['FormPage'].run_button.config(state='disabled')
            thread1 = threading.Thread(target=root.bar.start)
            thread2 = threading.Thread(target=lambda: set_info(ws, form_elements['email'], form_elements['keywords'],
                                                               genes, root))
            thread1.start()
            thread2.start()
        except Exception as e:
            tkinter.messagebox.showerror(title='Error',
                                         message='The process was interrupted, but your file was saved.\n' + str(e))
            if ".xlsx" == save_as_name[-5:]:
                save_as = save_as_name
            else:
                save_as = save_as_name + ".xlsx"
            wb.save(save_as)
            sys.exit()

    except (AttributeError, IndexError) as e:
        tkinter.messagebox.showinfo(title="Column Error",
                                    message="Check advanced page column input. \n" + str(e))


def try_file(user_input):
    """Loops until user enters an xlsx file (with or without the extension) that exists in the specified directory and
    returns the workbook in the file."""
    user_input = str(user_input)
    if ".xlsx" == user_input[-5:]:
        file_name = user_input
    else:
        file_name = user_input + '.xlsx'
    return load_workbook(filename=file_name, data_only=True)


def read_sheet(ws, amt=None):
    """Reads all existing values from list of columns if amt is not specified, otherwise, it gets up to the amt
    parameter"""
    if amt is None:
        amt = ws.max_row - 1
    gene_rows = []
    for row in range(1, amt+2):
        cells = []
        for col in range(1, ws.max_column+1):
            cell = ws.cell(row=row, column=col).value
            cells.append(cell)
        gene_rows.append(cells)
    return gene_rows


def remove_duplicates(ws):
    """Removes duplicated rows and empty rows from worksheet"""
    global symbol_col_num, form_elements
    rows = read_sheet(ws)
    rows_no_duplicates = []
    [rows_no_duplicates.append(row) for row in rows if row not in rows_no_duplicates]
    rows = [row for row in rows_no_duplicates if len([data for data in row if data is not None]) > 1]
    if form_elements['column_letters'] == 'AUTO':
        if 'Gene symbol' in rows[0]:
            symbol_col_num = rows[0].index('Gene symbol')
        elif 'SYMBOL' in rows[0]:
            symbol_col_num = rows[0].index('SYMBOL')
        else:
            tkinter.messagebox.showinfo(title='Automatic column search could not find "Gene symbol" or "SYMBOL"' +
                                              ' in spreadsheet')
    else:
        if ' ' in form_elements['column_letters'][0]:
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check advanced page symbol column input for spaces.")
            return
        elif any(char.isdigit() for char in form_elements['column_letters'][0]):
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check advanced page symbol column input for numbers.")
            return

        # if every element in the column is None (empty)
        elif all(el is None for el in rows[ord(form_elements['column_letters'][0].lower()) - 97]):
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check that the advanced page symbol column input was in the " +
                                                "range of the spreadsheet.")
            return
        else:
            symbol_col_num = ord(form_elements['column_letters'][0].lower()) - 97
    rows = [row for row in rows if row[symbol_col_num] is not None]  # removes rows with no symbol
    return rows


def write_rows(rows, ws):
    r = 1
    for row in rows:
        c = 1
        for data in row:
            ws.cell(row=r, column=c).value = data
            c += 1
        r += 1


def get_aliases(gene_rows):
    """This converts the data from the rows into all of the gene's aliases. First it adds the symbol to the list of
    aliases, then it adds the synonyms (separated by semicolon) and returns all of the aliases of all the genes."""
    if form_elements['column_letters'] == 'AUTO':
        if 'Gene title' in gene_rows[0]:
            synonyms_col_num = gene_rows[0].index('Gene title')
        elif 'SYNONYMS' in gene_rows[0]:
            synonyms_col_num = gene_rows[0].index('SYNONYMS')
        else:
            tkinter.messagebox.showinfo(title='Automatic column search could not find "Gene symbol" or "SYMBOL"' +
                                              ' in spreadsheet')
    else:
        if ' ' in form_elements['column_letters'][1]:
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check advanced page symbol column input for spaces.")
            return
        elif any(char.isdigit() for char in form_elements['column_letters'][1]):
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check advanced page symbol column input for numbers.")
            return

        # if every element in the column is None (empty)
        elif all(el is None for el in
                 [row[ord(form_elements['column_letters'][1].lower()) - 97] for row in gene_rows]):
            tkinter.messagebox.showinfo(title='Column Error',
                                        message="Check that the advanced page symbol column input was in the " +
                                                "range of the spreadsheet.")
            return
        else:
            synonyms_col_num = ord(form_elements['column_letters'][1].lower()) - 97
    gene_aliases = []
    for gene in gene_rows[1:]:
        if type(gene[symbol_col_num]) == datetime.datetime:
            aliases = []
        else:
            aliases = gene[symbol_col_num].split('///')  # symbols column is added to the list of names
        if gene[synonyms_col_num] is not None:
            synonyms = gene[synonyms_col_num].split("; ")
            aliases.extend(synonyms)
        gene_aliases.append(aliases)
    return gene_aliases


def set_info(ws, email, keywords, genes, root):
    """
    Writes TOTAL COUNT column and %keyword% COLUMN (helper function _write_info), as well as descriptions and sorting
    if these options are selected by the user.
    """
    global pb_int, form_elements
    quick_save = False
    all_counts = []
    number = 1
    for aliases in genes:  # for each list of aliases (one gene) in the full list of genes
        if ask_quit:
            print("Quitting...")
            sys.exit()
        if ask_save_and_quit:
            quick_save = True
            print("Saving...")
            break
        print("#%d" % number)

        # makes sure no aliases are common words that throw off the search
        aliases = [alias for alias in aliases if len(alias) > 2]
        counts = get_count(aliases, keywords, email)
        # the length of the list counts returned is the length of keywords + 1
        if len(counts) < 2:  # if counts list is not complete
            quick_save = True
            break
        else:
            print(counts)
            all_counts.append(counts)
            number += 1

    ws, rows = _write_info(ws, all_counts, keywords)

    if not quick_save:
        if form_elements['sort']:
            ws, rows = sort_ws(rows)

        # sets the ratio column
        col = total_count_col + 2
        ws.column_dimensions[_get_column_letter(col)].width = 16
        ws.cell(row=1, column=col).value = "COUNT RATIO"
        row = 2
        all_counts = sorted(all_counts, key=lambda el: int(el[0]))  # sorts all_counts so it matches the sorted file
        for counts in all_counts:
            try:
                count = int(counts[1]) / int(counts[0])
            except ZeroDivisionError:
                count = 0  # divide by zero error always means 0/0
            ws.cell(row=row, column=col).value = count
            row += 1

        if form_elements['descriptions']:
            print("Getting descriptions...")
            symbols_list = [row[symbol_col_num] for row in rows[1:]]
            row = 2
            for i, symbol in enumerate(symbols_list):
                if ask_quit:
                    sys.exit()
                pb_int += 1
                if symbol != '':
                    try:
                        comment = Comment(get_summary(symbol), "PubMed")
                        comment.width = '1000'  # TODO see if this works
                        comment.height = '1000'
                        ws.cell(row=row, column=symbol_col_num+1).comment = comment
                    except Exception as e:
                        tkinter.messagebox.showerror(title='Error',
                                                     message='Getting descriptions was interrupted by an error, ' +
                                                             'but your spreadsheet was saved.')
                        print(str(e))
                        break
                row += 1

    else:
        print("Quick save")

    wb.save(save_as_name)

    print("Done!")
    if tkinter.messagebox.showinfo(title='Success',
                                   message="Your file is located in " + os.path.dirname(filename)) == 'ok':
        root.bar.pb.grid_forget()
        root.custom_frames['FormPage'].run_button.config(state='enabled')
        root.custom_frames['AdvancedPage'].b3.config(state='enabled')
        pb_int = 0


def get_count(aliases, keywords, email):
    """Returns the number of times the gene comes up on PubMed. In the first try loop, the code decides whether it is
    getting the total count or narrow count. If it is the second time and the total count was 0, then the narrow count
    is automatically 0 so it will lessen the number of queries sent to PubMed. The try statement's purpose is to except
    a TypeError in case there is a mistake in the list (i.e. a date). Then the query is sent to PubMed and it gets the
    "Count" line."""
    global pb_int
    Entrez.email = email
    counts = []  # first number is total, second number is narrowed by keyword, third number is next keyword, etc
    for i in range(2):  # if len(keywords) > 1 else range(1)
        pb_int += 1  # increment the progressbar which will update as the other thread runs
        try:
            if i == 0:
                query = " OR ".join(aliases)
            elif counts[0] == "0":
                counts.append("0")
                continue  # if total count is 0, then narrow count is automatically 0
            else:
                query = "(%s) AND %s" % (" OR ".join(aliases), " AND ".join(keywords))
        except TypeError:  # if the gene name is in the wrong format (like if a date is entered accidentally)
            counts.append("0")
            continue

        try:
            handle = Entrez.egquery(term=query)
        except URLError as e:
            print(str(e))
            time.sleep(5)  # if there PubMed blocks the queries then it will wait for 5 seconds and try again
            try:
                handle = Entrez.egquery(term=query)
            except Exception as e:
                tkinter.messagebox.showwarning(title="Error", message=str(e)+" Your partial output has been saved.")
                return counts
        print(query)
        record = Entrez.read(handle)
        for row in record["eGQueryResult"]:
            counts.append(row["Count"])
            break
    time.sleep(.5)
    return counts


def _write_info(ws, all_counts, keywords):
    ws.column_dimensions[_get_column_letter(total_count_col)].width = 16

    ws.cell(row=1, column=total_count_col).value = "TOTAL COUNT"
    ws.column_dimensions[_get_column_letter(total_count_col+1)].width = 16
    ws.cell(row=1, column=total_count_col+1).value = '"%s" COUNT' % "/".join(keywords)  # to title the columns
    row = 2
    for counts in all_counts:
        col = total_count_col
        for count in counts:
            ws.cell(row=row, column=col).value = int(count)  # for each count loop it will move one row down
            col += 1
        row += 1

    rows = read_sheet(ws)
    return ws, rows


def sort_ws(rows):
    """Sorts the file's genes into a list of tuples"""
    ws = wb.active
    header = rows[0]
    gene_rows = rows[1:]
    gene_rows.sort(key=lambda x: x[total_count_col - 1])  # sorts genes by "Total Count" column
    row = 2
    for gene in gene_rows:
        col = 1
        for cell in gene:
            # writes sorted gene dictionary into the file to replace the existing values
            ws.cell(row=row, column=col).value = cell
            col += 1
        row += 1
    rows = [header]
    rows.extend(gene_rows)
    return ws, rows


def get_summary(symbol):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    mg = mygene.MyGeneInfo()
    try:
        entrez_id = mg.query('symbol:%s' % symbol, species='human')['hits'][0]['entrezgene']
    except (KeyError, IndexError):
        return "No entries found. (Entrez ID not found)"

    url = 'http://www.ncbi.nlm.nih.gov/gene/' + str(entrez_id)
    response = requests.get(url, version)
    html_output = response.text

    search_string_start = '<dt>Summary</dt>'
    match_start = html_output.find(search_string_start)
    if match_start != -1:
        match_start += len(search_string_start)
        html_output = html_output[match_start:]

        search_string_end = '<dt>Orthologs</dt>'
        match_end = html_output.find(search_string_end)
        if match_end != -1:
            html_output = html_output[:match_end]
            extract_string = re.sub('<[^<]+?>', '', html_output)  # takes out the HTML tags
        else:
            extract_string = "No entries found. (match_end = -1)"

    else:
        extract_string = "No entries found. (match_start= -1)"
    return extract_string


def main():
    root = layout.Window('BioDataSorter')
    root.geometry(str(layout.WINDOW_WIDTH) + 'x' + str(layout.WINDOW_HEIGHT) + '+300+300')
    root.mainloop()

if __name__ == '__main__':
    main()
