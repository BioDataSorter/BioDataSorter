from tkinter import *
from tkinter import font
import tkinter.colorchooser
import tkinter.filedialog
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import webbrowser
import configparser
import getpass

import openpyxl
from PIL import Image, ImageTk  # in project requirements as 'Pillow'

import main
import makecloud
# from HoverInfo import HoverText

HEAD = ("Arial", 16)
FONT = ("Arial", 10)
COURIER = ("Courier New", 12)

WINDOW_WIDTH = 570
WINDOW_HEIGHT = 440
NOTEBOOK_WIDTH = 400
NOTEBOOK_HEIGHT = 280

NOTEBOOK_COLOR = 'white'

GUI_DEBUG = False


class Window(Tk):

    def __init__(self, title, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.wm_resizable(0, 0)
        self.title(title)
        self.wm_iconbitmap("images\doublehelix.ico")
        self.messages = ["Start a new process, convert a GEO text file to "
                         "Excel, or play with settings.",  # File
                         "Edit the main form or reset both forms.",  # Edit
                         "Toggle the status bar.",  # View
                         "Stop to stop running program then exit for quick "
                         "exit.",
                         "Plot a word cloud of an output file based on the "
                         "number of citations from PubMed.",  # Graph
                         "Edit the advanced menu."]  # Advanced
        self.bg_color = 'powder blue'

        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)

        # sub_container for options bar
        self.sub_container = Frame(self.container)
        self.sub_container.pack(side=TOP, expand=TRUE, fill=BOTH)

        self.side_bar = OptionsBar(self.sub_container, self)
        self.side_bar.grid(column=0, rowspan=3, padx=(10, 0), pady=10)

        self.pb_space = Frame(self.sub_container, {'height': 50,
                                                   'width': 500,
                                                   'background': 'red'})

        # pady 2nd param also controls status bar placement
        # if the window was resizable it would be placed incorrectly
        self.pb_space.grid(row=7, columnspan=3, pady=(15, WINDOW_HEIGHT -
                                                      NOTEBOOK_HEIGHT - 150))
        self.pb_space.pack_propagate(0)
        self.key = Key(self.pb_space, {'background': 'white',
                                       'highlightthickness': '4',
                                       'highlightcolor': 'gray90'})

        self.bar = ProgressWin(self.pb_space, self)

        self.status_bar = StatusBar(self.container)
        self.status_bar.pack(side="bottom", fill=X, expand=True, anchor='s')
        self.status_bar.set("Ready")

        # =================
        # NOTEBOOK AND TABS
        # =================

        self.nbk = ttk.Notebook(self.sub_container, width=NOTEBOOK_WIDTH,
                                height=NOTEBOOK_HEIGHT)

        # contains ttk.Frame type for adding and showing frames
        self.frames = {}
        self.custom_frames = {}  # contains custom types for accessing elements

        # AdvancedPage is before FormPage because FormPage init needs to access
        # its methods (save and import_entries)
        for F in (StartPage, AdvancedPage, FormPage, OutputPage):
            frame = ttk.Frame(self.nbk)
            custom = F(frame, self, {'background': NOTEBOOK_COLOR,
                                     'highlightthickness': '4',
                                     'highlightcolor': 'gray90'})
            custom.pack(expand=True, fill=BOTH, side=TOP)
            custom.tkraise()

            # instead of the class as the key, the string is the key
            self.frames[str(F)[15:-2]] = frame
            self.custom_frames[str(F)[15:-2]] = custom

        self.nbk.grid(row=1, column=1, sticky='nsew', padx=(0, 20), pady=(20,
                                                                          5))

        # ========
        # MENU BAR
        # ========

        self.menubar = Menu(self)

        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New Process",
                             command=lambda: self.show_frame('FormPage'))
        filemenu.add_command(label="Convert", command=self.convert)

        filemenu.add_separator()

        settingsmenu = Menu(filemenu, tearoff=0)
        settingsmenu.add_command(label="Change Color",
                                 command=self.change_color)

        advanced_page_ = self.custom_frames['AdvancedPage']
        settingsmenu.add_command(label="Import Settings",
                                 command=advanced_page_.import_settings)
        settingsmenu.add_command(label="Save Settings",
                                 command=advanced_page_.save_settings)
        filemenu.add_cascade(label="Settings", menu=settingsmenu)

        entriesmenu = Menu(filemenu, tearoff=0)
        entriesmenu.add_command(label="Import Entries",
                                command=advanced_page_.import_entries)
        entriesmenu.add_command(label="Save Entries",
                                command=advanced_page_.save)
        filemenu.add_cascade(label="Entries", menu=entriesmenu)

        self.menubar.add_cascade(label="File", menu=filemenu)  # index = 0

        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Main Form",
                             command=lambda: self.show_frame('FormPage'))
        editmenu.add_command(label="Reset", command=self.reset)
        self.menubar.add_cascade(label="Edit", menu=editmenu)  # index = 1

        self.show_status = BooleanVar()
        self.show_status.set(True)
        viewmenu = Menu(self.menubar, tearoff=0)
        viewmenu.add_checkbutton(label="Status bar",
                                 command=self.status_bar_toggle,
                                 variable=self.show_status,
                                 onvalue=True,
                                 offvalue=False)
        self.menubar.add_cascade(label="View", menu=viewmenu)  # index = 2

        runmenu = Menu(self.menubar, tearoff=0)
        runmenu.add_command(label="Run Process",
                            command=lambda: main.get_entries(self))
        runmenu.add_command(label="Save and Stop", command=self.save_and_quit)
        runmenu.add_command(label="Stop", command=self.complete)
        runmenu.add_command(label="Exit", command=sys.exit)
        self.menubar.add_cascade(label="Run", menu=runmenu)

        graphmenu = Menu(self.menubar, tearoff=0)
        graphmenu.add_command(label="Word Cloud", command=self.display_cloud)
        self.menubar.add_cascade(label="Graph", menu=graphmenu)

        advancedmenu = Menu(self.menubar, tearoff=0)
        advancedmenu.add_command(label="Options", command=
                                 lambda: self.show_frame('AdvancedPage'))
        self.menubar.add_cascade(label="Advanced", menu=advancedmenu)

        self.config(menu=self.menubar)
        self.menubar.bind('<<MenuSelect>>', self.status_bar_update)

        # ==========
        # POPUP MENU
        # ==========

        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label='Close', command=self.close_tab)
        self.popup.add_command(label='Open All Tabs',
                               command=self.open_all_tabs)
        self.popup_index = None

        self.frame_indexes = {}
        self.current_frame = None
        self.add_frame('StartPage')

        self.update_color()

    def status_bar_toggle(self):
        if self.status_bar.label.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side="bottom", fill="both", expand=True)

    def status_bar_update(self, event=None):
        index = self.call(event.widget, "index", "active")
        if index in range(0, len(self.messages)):
            self.status_bar.set(self.messages[index])
        else:
            self.status_bar.set("Ready")

    def show_frame(self, cont):
        if cont == 'AdvancedPage' and \
                        str(self.frames['FormPage']) not in self.nbk.tabs():
            self.show_frame('FormPage')
        if str(self.frames[cont]) not in self.nbk.tabs():
            self.add_frame(cont)
        self.nbk.select(self.frame_indexes[cont])
        self.current_frame = cont

    def add_frame(self, cont):
        frame = self.frames[cont]  # shows the frame that is called by class
        self.nbk.add(frame, text=cont[:-4])
        self.frame_indexes[cont] = self.nbk.index('end') - 1
        self.nbk.bind('<Button-3>', self.on_button_3)

    def on_button_3(self, event):
        if event.widget.identify(event.x, event.y) == 'label':
            self.popup_index = event.widget.index('@%d,%d' % (event.x, event.y))
            try:
                self.popup.tk_popup(event.x_root + 57, event.y_root + 11, 0)
            finally:
                self.popup.grab_release()

    def close_tab(self):

        # if there is more than one tab open
        if self.nbk.index('end') > 1 and self.popup_index is not None:
            self.nbk.hide(self.popup_index)
            self.popup_index = None

    def open_all_tabs(self):
        tabs = ['StartPage', 'FormPage', 'AdvancedPage']
        for tab in tabs:
            self.show_frame(tab)

    def change_color(self, color=None):
        if color is not None:
            self.bg_color = color
        else:
            self.bg_color = tkinter.colorchooser.askcolor()[1]
        self.update_color()

    def update_color(self):
        if not GUI_DEBUG:
            self.side_bar['bg'] = self.bg_color
            self.container['bg'] = self.bg_color
            self.sub_container['bg'] = self.bg_color
            self.pb_space['bg'] = self.bg_color

    def reset(self):
        self.bg_color = 'powder blue'
        self.update_color()

        self.custom_frames['FormPage'].set_filename("Select file...")
        main.form_elements['filename'] = None
        self.custom_frames['FormPage'].ents["Email"].delete(0, END)
        self.custom_frames['FormPage'].ents["Keywords"].delete(0, END)
        self.custom_frames['FormPage'].v2.set("Select file...")
        main.form_elements['filename'] = None

        advanced_page_ = self.custom_frames['AdvancedPage']
        advanced_page_.auto_manual_columns.set('AUTO')
        advanced_page_.symbol_col.delete(0, END)
        advanced_page_.symbol_col.config(state='disabled')
        advanced_page_.synonyms_col.delete(0, END)
        advanced_page_.synonyms_col.config(state='disabled')
        advanced_page_.v.set("ALL")
        advanced_page_.entry.delete(0, END)
        advanced_page_.entry.config(state="disabled")
        advanced_page_.desc.set(0)
        advanced_page_.sort.set(0)

    def convert(self):
        root = ConvertPrompt(self)
        root.mainloop()

    def display_cloud(self):
        output_file = makecloud.generate_word_cloud()
        self.show_frame('OutputPage')
        self.custom_frames['OutputPage'].display_image(output_file)

    def show_key(self):
        self.key.fill_in()
        self.key.pack(side='bottom', fill='both', expand=True)

    @staticmethod
    def complete():
        main.ask_quit = True

    @staticmethod
    def save_and_quit():
        main.ask_save_and_quit = True


class ConvertPrompt(Toplevel):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Convert File")
        self.master = master

        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialdir'] = "C:\\Users\\%s\\" % getpass.getuser()
        options['parent'] = master
        options['title'] = "Choose a file"

        self.grid_columnconfigure(1, weight=1)
        msg = Label(self, text="Convert tab delineated .txt to .xlsx.")
        msg.grid(row=0, columnspan=3, pady=(10, 4), padx=5)
        lab = Label(self, text="Text file: ")
        lab.grid(row=1, column=0, padx=5)

        # this stores the displayed version of the filename
        self.v_display = StringVar()
        b1 = ttk.Button(self, text="Browse...", command=self.askopenfilename)
        b1.grid(row=1, column=1, padx=5)
        self.geometry('190x80+300+300')

    def askopenfilename(self):
        file = tkinter.filedialog.askopenfilename(**self.file_opt)
        if not file:
            return
        with open(file, 'r') as f:
            unsplit_rows = f.read().split('\n')
        split_rows = []
        for row in unsplit_rows:
            split_rows.append(row.split('\t'))
        converted_wb = openpyxl.Workbook()
        ws_input = converted_wb.active
        ws_input.title = 'Input'
        main.write_rows(split_rows, ws_input)
        save_name = file[:-4] + '.xlsx'
        # TODO program gives error "select a file to sort" even though the
        # words are displayed
        try:
            converted_wb.save(save_name)

        # if the user tries to save it in C: or somewhere inaccessible
        except PermissionError:
            # it will be saved in the current directory
            converted_wb.save(save_name.split('/')[-1])
        self.master.show_frame('FormPage')
        self.master.custom_frames['FormPage'].set_filename(save_name)

        self.destroy()


class StatusBar(Frame):

    def __init__(self, master):
        super().__init__(master)
        Frame.__init__(self, master, background='gray88')
        self.text = StringVar()
        self.label = Label(self,
                           anchor=W,
                           background='gray88',
                           textvariable=self.text,
                           foreground='dark slate gray')
        self.label.pack(fill=X, side=BOTTOM)

    def set(self, status):
        self.text.set(status)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text='')
        self.label.update_idletasks()


class OptionsBar(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent)
        Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller

        info_image = ".\images\Information.png"
        self.b1, self.photo = self.button_from_label("Info",
                                                     info_image,
                                                     self.info_button,
                                                     "Get information and help"
                                                     " about new features")
        self.b1.grid(row=0, padx=(20, 0), pady=15)

        self.b2, self.photo2 = self.button_from_label("New",
                                                      ".\images\Search.png",
                                                      self.new_button,
                                                      "Process another input "
                                                      "file to get citations.")
        self.b2.grid(row=1, padx=(20, 0), pady=15)

    def button_from_label(self, text, image_url, cmd, status):
        image = Image.open(image_url)
        image = image.resize((30, 30), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        btn = Label(self,
                    text=text,
                    image=photo,
                    compound=TOP,
                    width=70,
                    bg=NOTEBOOK_COLOR,
                    cursor='hand2')
        btn.bind('<Button-1>', cmd)
        btn.bind('<Enter>', lambda e: (btn.config(bg='light cyan'),
                                       self.controller.status_bar.set(status)))
        btn.bind('<Leave>', lambda e:
                 (btn.config(bg=NOTEBOOK_COLOR),
                  self.controller.status_bar.set('Ready')))
        btn.bind('<ButtonRelease-1>', lambda e: btn.config(bg='light cyan'))
        return btn, photo

    def info_button(self, _):
        self.b1.config(bg='LightSlateGray')
        self.controller.show_frame('StartPage')

    def new_button(self, _):
        self.b2.config(bg='LightSlateGray')
        self.controller.show_frame('FormPage')
        

class StartPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super(StartPage, self).__init__(parent, *args, **kwargs)
        # Frame.__init__(parent, *args, **kwargs)
        padding_x = round(NOTEBOOK_WIDTH / 7)
        padding_y = round(NOTEBOOK_HEIGHT / 9)
        self.controller = controller
        self.previous_color = controller.bg_color

        lab = Label(self, text="Welcome to BioDataSorter", font=HEAD,
                    background=NOTEBOOK_COLOR, cursor='heart')
        lab.grid(row=0, padx=padding_x, pady=padding_y)
        # lab.bind('<Button-1>', self.surprise_color)
        lab.bind('<Leave>', lambda e:
                 # current color is reset
                 (controller.change_color(self.previous_color),
                  controller.status_bar.set('Ready')))

        get_started = Label(self,
                            text="Click New to get started or File>Convert \n "
                                 "a text file from GEO profile data.",
                            background='white',
                            font=FONT)
        get_started.grid(row=1, pady=(0, 85))

        separator = Frame(self, height=1, width=NOTEBOOK_WIDTH, bg='dark gray')
        separator.grid(row=2, pady=(0, 10))

        underline = font.Font(font="arial 10 underline italic")
        self.github_link = "https://github.com/BioDataSorter/BioDataSorter"

        self.copy_link_popup = Menu(controller, tearoff=0)
        cb_append = controller.clipboard_append
        self.copy_link_popup.add_command(label='Copy Link',
                                         command=lambda:
                                         cb_append(self.github_link))
        self.copy_link_popup.add_command(label='Open Link in Browser',
                                         command=self.launch_page)

        lab2 = Label(self,
                     text="Visit our GitHub repository for more information",
                     background=NOTEBOOK_COLOR,
                     cursor='hand2',
                     font=underline)
        lab2.grid(row=3)
        lab2.bind('<Enter>', lambda e: (lab2.config(foreground='blue'),
                                        controller.status_bar.set(
                                            self.github_link)))
        lab2.bind('<Leave>', lambda e: (lab2.config(foreground='black'),
                                        controller.status_bar.set('Ready')))
        lab2.bind('<Button-1>', self.launch_page)
        lab2.bind('<Button-3>', self.on_button_3)

    def launch_page(self, _=None):
        webbrowser.open_new_tab(self.github_link)

    def surprise_color(self, _):
        self.previous_color = self.controller.bg_color
        self.controller.change_color('red')
        self.controller.status_bar.set('Awww... we love you too!')

    def on_button_3(self, event):
        try:
            self.copy_link_popup.tk_popup(event.x_root + 75,
                                          event.y_root + 11,
                                          0)
        finally:
            self.copy_link_popup.grab_release()


class FormPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Frame.__init__(parent, *args, **kwargs)

        self.controller = controller
        self.file_opt = options = {}
        options['defaultextension'] = '.xlsx'
        options['filetypes'] = [('excel files', '.xlsx')]
        options['initialdir'] = "C:\\Users\\%s\\" % getpass.getuser()
        options['parent'] = controller
        options['title'] = "Choose a file"

        self.popup = Menu(controller, tearoff=0)
        self.popup.add_command(label='Run',
                               command=lambda: main.get_entries(controller))
        self.popup.add_command(label='More Options',
                               command=lambda:
                               controller.show_frame('AdvancedPage'))

        self.popup.add_separator()
        advanced_page_ = controller.custom_frames['AdvancedPage']
        self.popup.add_command(label='Import Entries',
                               command=advanced_page_.import_entries)
        self.popup.add_command(label='Save Entries',
                               command=advanced_page_.save)

        # ===============Form buttons and text fields=========================
        main_form = Frame(self, background=NOTEBOOK_COLOR,
                          width=NOTEBOOK_WIDTH)
        main_form.grid_columnconfigure(0, weight=1)
        lab = Label(main_form, text="File: ", background=NOTEBOOK_COLOR)
        lab.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        b1 = ttk.Button(main_form,
                        text="Browse...",
                        cursor='hand2',
                        command=self.askopenfilename)
        b1.grid(row=0, column=2, sticky=E, padx=5, pady=5)
        self.ents, make_form_widgets = make_form(main_form, 1,
                                                 ['Email', 'Keywords'])

        make_form_widgets[-1].bind('<Return>',
                                   lambda e: main.get_entries(controller))

        lab2 = Label(main_form, text="Save As: ", background=NOTEBOOK_COLOR)
        lab2.grid(row=3, column=0, sticky=W, padx=5, pady=5)

        b2 = ttk.Button(main_form,
                        text="Browse...",
                        cursor='hand2',
                        command=self.asksaveasfilename)
        b2.grid(row=3, column=2, sticky=E, padx=5, pady=5)

        self.v = StringVar()  # input file name
        self.v_display = StringVar()
        self.set_filename("Select file...")
        lab3 = Label(main_form, textvariable=self.v_display,
                     background=NOTEBOOK_COLOR)
        lab3.grid(row=0, column=1, padx=5, pady=5)
        lab3.bind('<Enter>', lambda e: controller.status_bar.set(self.v.get()))
        lab3.bind('<Leave>', lambda e: controller.status_bar.set('Ready'))

        self.v2 = StringVar()  # save as name
        self.v2_display = StringVar()
        self.set_savename("Select file...")
        lab4 = Label(main_form, textvariable=self.v2_display,
                     background=NOTEBOOK_COLOR)
        lab4.grid(row=3, column=1, padx=5, pady=5)
        lab4.bind('<Enter>',
                  lambda e: controller.status_bar.set(self.v2.get()))
        lab4.bind('<Leave>', lambda e: controller.status_bar.set('Ready'))

        main_form.pack(fill=X)

        # ===========bottom buttons "More Options" and "Run"==================
        buttons_frame = Frame(self, background=NOTEBOOK_COLOR)
        buttons_frame.pack(side=BOTTOM, pady=(0, 15))

        options_button = ttk.Button(buttons_frame, text="More Options",
                                    command=lambda:
                                    controller.show_frame('AdvancedPage'))
        self.run_button = ttk.Button(buttons_frame, text="Run",
                                     command=lambda:
                                     main.get_entries(controller))
        options_button.grid(row=0, column=0, padx=5, pady=10, sticky=S)
        self.run_button.grid(row=0, column=1, padx=5, pady=10, sticky=S)

        make_form_widgets.extend([self, lab, lab2, lab3, lab4])
        widgets = make_form_widgets

        add_tag('form_elements', widgets)
        self.bind_class('form_elements', '<Button-3>', self.on_button_3)

    def askopenfilename(self):
        file = tkinter.filedialog.askopenfilename(**self.file_opt)
        if file:
            main.form_elements['filename'] = file
            self.set_filename(file)

    def asksaveasfilename(self):
        file = tkinter.filedialog.asksaveasfile(**self.file_opt)
        if file:
            main.form_elements['save_as_name'] = file.name
            self.set_savename(file.name)

    def on_button_3(self, event):
        try:
            self.popup.tk_popup(event.x_root + 55, event.y_root + 11, 0)
        finally:
            self.popup.grab_release()

    def set_filename(self, string):
        self.v.set(string)
        string = string.split('/')[-1]
        if len(string) > 20:
            self.v_display.set(string[:20] + '...')
        else:
            self.v_display.set(string)

    def set_savename(self, string):
        self.v2.set(string)
        string = string.split('/')[-1]
        if len(string) > 20:
            self.v2_display.set(string[:20] + '...')
        else:
            self.v2_display.set(string)


class AdvancedPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent,  *args, **kwargs)
        # Frame.__init__(parent, *args, **kwargs)
        self.controller = controller
        self.grid_columnconfigure(1, weight=1)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        s = ttk.Style()
        s.configure("White.TRadiobutton", background=NOTEBOOK_COLOR)
        s.configure("White.TCheckbutton", background=NOTEBOOK_COLOR)

        get_columns_lab = Label(self,
                                text="'Gene Symbol' and 'Gene Title' Column "
                                     "Letters:",
                                background=NOTEBOOK_COLOR)
        get_columns_lab.grid(row=0, columnspan=3, pady=5)

        self.auto_manual_columns = StringVar()
        self.auto_manual_columns.set('AUTO')
        rb_auto = ttk.Radiobutton(self,
                                  text="Get automatically",
                                  variable=self.auto_manual_columns,
                                  value='AUTO',
                                  command=self.disable_columns_ents,
                                  style='White.TRadiobutton')
        rb_manual = ttk.Radiobutton(self,
                                    text="Manual input",
                                    variable=self.auto_manual_columns,
                                    value='MANUAL',
                                    command=self.manual_on_click,
                                    style='White.TRadiobutton')
        rb_auto.grid(row=1, column=0)
        rb_manual.grid(row=1, column=1, sticky=E)

        self.symbol_col = ttk.Entry(self, width=17, state='disabled',
                                    style='EntryStyle.TEntry')
        symbol_tags = self.symbol_col.bindtags() + ('columntag',)
        self.symbol_col.bindtags(symbol_tags)
        self.symbol_col.grid(row=1, column=2, sticky=W, padx=(0, 5))

        self.synonyms_col = ttk.Entry(self, width=17, state='disabled',
                                      style='EntryStyle.TEntry')
        synonyms_tags = self.synonyms_col.bindtags() + ('columntag',)
        self.synonyms_col.bindtags(synonyms_tags)
        self.synonyms_col.grid(row=2, column=2, sticky=W, padx=(0, 5), pady=5)

        self.bind_class('columntag', '<FocusIn>',
                        lambda e: e.widget.delete(0, END))
        self.bind_class('columntag', '<FocusOut>',
                        lambda e: self.manual_on_click())
        self.bind_class('columntag', '<Button-1>', self.column_ents_click)
        self.symbol_col.bind('<Enter>',
                             lambda e:
                             controller.status_bar.set("Change the 'Gene "
                                                       "Symbol' or 'SYMBOL'"
                                                       " column manually"))
        self.synonyms_col.bind('<Enter>', lambda e:
                               controller.status_bar.set("Change the 'Gene "
                                                         "Title' or 'SYNONYMS'"
                                                         " column manually"))
        self.bind_class('columntag', '<Leave>',
                        lambda e: controller.status_bar.set('Ready'))

        separator = Frame(self, height=1, width=NOTEBOOK_WIDTH, bg='dark gray')
        separator.grid(row=3, columnspan=3, pady=(10, 0))

        lab = Label(self, text="Number of Genes to Use:",
                    background=NOTEBOOK_COLOR)
        lab.grid(row=4, columnspan=3, sticky=W, padx=5, pady=(10, 0))

        self.v = StringVar()
        self.v.set("ALL")
        rb = ttk.Radiobutton(self, text="All", variable=self.v, value="ALL",
                             command=self.disable_entry,
                             style="White.TRadiobutton")
        rb2 = ttk.Radiobutton(self, text="Top x genes", variable=self.v,
                              value="SELECT", command=self.enable_entry,
                              style="White.TRadiobutton")
        self.entry = ttk.Entry(self, width=10, state="disabled",
                               style="EntryStyle.TEntry")
        self.entry.bind('<Button-1>', self.entry_click)
        self.entry.bind('<Enter>',
                        lambda e:
                        controller.status_bar.set("Process only a portion of "
                                                  "the spreadsheet."))
        self.entry.bind('<Leave>',
                        lambda e: controller.status_bar.set('Ready'))

        rb.grid(row=5, column=0, sticky=W, padx=5, pady=5)
        rb2.grid(row=5, column=1, sticky=E, padx=5, pady=5)
        self.entry.grid(row=5, column=2, sticky=W, pady=5, padx=(0, 5))

        self.desc = IntVar()  # if desc is 1, then it is checked
        self.sort = IntVar()  # if sort is 1, then it is checked

        c = ttk.Checkbutton(self, text="Add descriptions", variable=self.desc,
                            style="White.TCheckbutton")
        c.grid(row=6, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        c.bind('<Enter>',
               lambda e: controller.status_bar.set("Get descriptions of the "
                                                   "gene symbols from "
                                                   "PubMed."))
        c.bind('<Leave>', lambda e: controller.status_bar.set('Ready'))

        c2 = ttk.Checkbutton(self, text="Sort", variable=self.sort,
                             style="White.TCheckbutton")
        c2.grid(row=6, column=2, sticky=W, padx=5, pady=5)
        c2.bind('<Enter>',
                lambda e: controller.status_bar.set("Sort the output file by "
                                                    "the total number of "
                                                    "citations found."))
        c2.bind('<Leave>', lambda e: controller.status_bar.set('Ready'))

        buttons_frame = Frame(self, background=NOTEBOOK_COLOR)
        buttons_frame.grid(row=7, columnspan=3)

        b1 = ttk.Button(buttons_frame, text="Import Entries",
                        command=self.import_entries)
        b1.grid(row=0, column=0, padx=5, pady=5)
        b2 = ttk.Button(buttons_frame, text="Save Entries", command=self.save)
        b2.grid(row=0, column=1, padx=5, pady=5)
        self.b3 = ttk.Button(buttons_frame, text="Run",
                             command=lambda: main.get_entries(controller))
        self.b3.grid(row=0, column=2, padx=5, pady=5)

        for widget in [rb, rb2, self.entry, c, c2, b2, self.b3]:
            widget.bind('<FocusIn>', self.deselect_manual)

    def entry_click(self, _):
        self.v.set("SELECT")
        self.enable_entry()

    def enable_entry(self):
        self.entry.configure(state="normal")

    def disable_entry(self):
        self.entry.delete(0, END)
        self.entry.configure(state="disabled")

    def disable_columns_ents(self):
        self.symbol_col.delete(0, END)
        self.synonyms_col.delete(0, END)
        self.symbol_col.configure(state='disabled')
        self.synonyms_col.configure(state='disabled')

    def manual_on_click(self):
        self.symbol_col.configure(state='normal')
        self.synonyms_col.configure(state='normal')
        if self.symbol_col.get() == '' or self.symbol_col.get() is None:
            self.symbol_col.insert(0, 'Gene symbol Col')
        if self.synonyms_col.get() == '' or self.synonyms_col.get() is None:
            self.synonyms_col.insert(0, 'Gene title Col')

    def column_ents_click(self, _):
        self.auto_manual_columns.set('MANUAL')
        self.manual_on_click()

    def deselect_manual(self, event):
        disallowed = ['', 'Gene symbol Col', 'Gene title Col']
        if self.symbol_col.get() in disallowed or \
                self.synonyms_col.get() in disallowed:
            self.auto_manual_columns.set('AUTO')
            self.disable_columns_ents()

    def save(self):
        print("saving")
        sections = ['main', 'advanced']
        for section in sections:
            if not self.config.has_section(section):
                self.config.add_section(section)

        self.config.set("advanced",
                        "Symbol Column",
                        "AUTO" if self.auto_manual_columns.get() == "AUTO"
                        else self.symbol_col.get())
        self.config.set("advanced",
                        "Synonyms Column",
                        "AUTO" if self.auto_manual_columns.get() == "AUTO"
                        else self.synonyms_col.get())
        self.config.set("advanced",
                        "Genes to Use",
                        "ALL" if self.v.get() == "ALL" else self.entry.get())
        self.config.set("advanced", "Descriptions", str(self.desc.get()))
        self.config.set("advanced", "Sort", str(self.sort.get()))

        self.config.set("main", "Filename",
                        '' if main.form_elements['filename'] is None
                        else main.form_elements['filename'])
        form_page_ = self.controller.custom_frames["FormPage"]
        self.config.set("main", "Email",
                        form_page_.ents["Email"].get())
        self.config.set("main", "Keywords", form_page_.ents["Keywords"].get())
        self.config.set("main", "Save As",
                        '' if main.form_elements['save_as_name'] is None else
                        main.form_elements['save_as_name'])

        with open("config.ini", "w") as f:
            self.config.write(f)

    def import_entries(self):
        try:
            config = self.config
            if config.get("advanced", "Symbol Column") == "AUTO" or \
                    config.get("advanced", "Synonyms Column") == "AUTO":
                self.auto_manual_columns.set('AUTO')
                self.symbol_col.delete(0, END)
                self.symbol_col.configure(state='disabled')
                self.synonyms_col.delete(0, END)
                self.synonyms_col.configure(state='disabled')
            else:
                self.auto_manual_columns.set('MANUAL')
                self.symbol_col.config(state='normal')
                self.symbol_col.delete(0, END)
                self.symbol_col.insert(0, config.get("advanced",
                                                     "Symbol Column"))

                self.synonyms_col.config(state='normal')
                self.synonyms_col.delete(0, END)
                self.synonyms_col.insert(0, config.get("advanced",
                                                       "Synonyms Column"))

            if config.get("advanced", "Genes to Use") == "ALL":
                self.v.set("ALL")
                self.entry.delete(0, END)
                self.entry.configure(state='disabled')
            else:
                self.v.set("SELECT")
                self.entry.config(state="normal")
                self.entry.delete(0, END)
                self.entry.insert(0, config.get("advanced",
                                                "Genes to Use"))
            self.desc.set(int(config.get("advanced", "Descriptions")))
            self.sort.set(int(config.get("advanced", "Sort")))

            main.form_elements['filename'] = config.get("main", "Filename") \
                if config.get("main", "Filename") != '' else None
            form_page_ = self.controller.custom_frames["FormPage"]
            form_page_.set_filename("Select file..."
                                    if config.get("main", "Filename") == ''
                                    else config.get("main",
                                                    "Filename").split('/')[-1])
            form_page_.ents["Email"].delete(0, END)
            form_page_.ents["Email"].insert(0, config.get("main", "Email"))
            form_page_.ents["Keywords"].delete(0, END)
            form_page_.ents["Keywords"].insert(0, config.get("main",
                                                             "Keywords"))
            main.form_elements['save_as_name'] = config.get("main", "Save As")\
                if config.get("main", "Save As") != '' else None
            form_page_.set_savename("Select file..." if
                                    config.get("main", "Save As") == ''
                                    else config.get("main",
                                                    "Save As").split('/')[-1])

        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            messagebox.showerror(title="Outdated config.ini",
                                 message="Config.ini file is invalid or "
                                         "outdated, please save settings "
                                         "again. " + str(e))

    def import_settings(self):
        try:
            self.controller.change_color(self.config.get("settings",
                                                         "Background Color"))
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

    def save_settings(self):
        if not self.config.has_section('settings'):
            self.config.add_section('settings')
        self.config.set("settings", "Background Color",
                        self.controller.bg_color)
        with open("config.ini", "w") as f:
            self.config.write(f)


class ProgressWin(Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.tasks = ["Idle", "Getting counts", "Getting descriptions"]
        self.current_task = self.tasks[0]

        self.pb = ttk.Progressbar(parent, orient='horizontal', length=400,
                                  mode='determinate')  # grid in start
        self.pb.bind('<Enter>',
                     lambda e: controller.status_bar.set(self.current_task))
        self.pb.bind('<Leave>', lambda e: controller.status_bar.set('Ready'))

        self.items = 0  # number of queries searched so far
        self.total_items = 0  # the total number of queries to be searched

    def start(self):
        self.pb.pack()
        self.current_task = self.tasks[1]
        self.pb['value'] = 0
        self.pb['maximum'] = main.total_queries
        self.load()

    def load(self):
        self.items = main.pb_int
        self.pb['value'] = self.items
        if main.form_elements['descriptions'] and \
                main.pb_int > main.total_queries * 2 / 3:
            self.current_task = self.tasks[2]

        if self.items < main.total_queries:
            self.after(1000, self.load)  # updates after 1 second


class OutputPage(Frame):
    """Frame within the notebook that displays the wordcloud output.
    
    Attributes:
        parent (ttk.Frame): The frame within the notebook window. It is
            organized by pack after each page is initialized.
        controller (Window): The overall frame containing all of the widgets.
            Also organized by pack.
    
    """

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.controller = controller
        self.wordcloud = Label(self)
        self.lab = Label(self, background=NOTEBOOK_COLOR)

    def display_image(self, image_url):
        if image_url is None:
            self.wordcloud.image = None
            self.controller.nbk.hide(self.parent)
            return
        screen_width = self.parent.winfo_width()
        screen_height = self.parent.winfo_height() - 40
        maxsize = (screen_width, screen_height)
        image = Image.open(image_url)
        resized = image.resize(maxsize, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized)
        self.wordcloud.config(image=photo, cursor='hand2')
        self.wordcloud.image = photo
        self.wordcloud.pack()
        if len(image_url) > 70:
            image_url_text = image_url[:65] + '...'
        else:
            image_url_text = image_url
        self.lab.config(text=image_url_text)
        self.lab.pack()
        self.controller.show_key()

        # hover_key = HoverText(self.lab, "Color Key: Ratio Column\n"
        #                                 "Red:First Quarter\n"
        #                                 "Yellow:Second Quarter\n"
        #                                 "Green:Third Quarter\n"
        #                                 "Blue:Fourth Quarter")
        self.wordcloud.bind('<Enter>',
                            lambda e: self.controller.status_bar.set(image_url)
                            )
        #                     hover_key.enter(e)))
        self.wordcloud.bind('<Leave>',
                            lambda e: self.controller.status_bar.set('Ready'))
        #                               hover_key.leave(e)))
        self.wordcloud.bind('<Button-1>', lambda e: self.open_image(image_url))
        # self.wordcloud.bind('<Motion>', hover_key.motion)

    def open_image(self, image_url):
        top = Toplevel(self)
        image = Image.open(image_url)
        photo = ImageTk.PhotoImage(image)
        expandable_cloud = Label(top, image=photo)
        expandable_cloud.image = photo
        expandable_cloud.pack()


class Key(Frame):

    BG_COLOR = 'black'
    FG_COLOR = 'white'
    FONT = ('TkDefaultFont', 20)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

    def fill_in(self):

        # get colors as a list from makecloud.py
        colors = list(makecloud.quartiles.keys())
        title = Frame(self, {'background': Key.BG_COLOR})
        label = Label(title,
                      text='Key (Ratios)',
                      font=FONT,
                      background=Key.BG_COLOR,
                      foreground=Key.FG_COLOR,
                      pady=10)
        label.pack()
        title.grid(row=0, column=0)

        # TODO loop each column
        quartiles = [makecloud.quartile1,
                     makecloud.median,
                     makecloud.quartile3,
                     len(makecloud.symbols) - 1]

        for i in range(4):
            col = Frame(self, {'background': Key.BG_COLOR})
            q_str = "0" if i == 0 \
                else str(round(makecloud.symbols[quartiles[i-1]][2], 4))
            q_str += " to "
            q_str += str(round(makecloud.symbols[quartiles[i]][2], 4))
            lab = Label(col, text=q_str,
                        font=FONT,
                        foreground=colors[i],
                        background=Key.BG_COLOR,
                        padx=5,
                        pady=10)
            lab.pack()
            col.grid(row=0, column=1+i)


def make_form(frame, row_start, fields):
    entries = {}
    widgets = []
    for field in fields:
        lab = Label(frame, text=field+": ", anchor='w',
                    background=NOTEBOOK_COLOR)
        ent = ttk.Entry(frame, style="Thistle.TEntry")
        lab.grid(row=row_start, column=0, sticky=W, padx=5, pady=5)
        ent.grid(row=row_start, column=1, columnspan=2, sticky="nsew", padx=5,
                 pady=5)

        widgets.extend([lab, ent])
        entries[field] = ent
        row_start += 1
    return entries, widgets


def add_tag(tag, args):
    """Adds the tag parameter as a bind tag for the other parameters
    (widgets)"""
    for widget in args:
        widget.bindtags((tag,) + widget.bindtags())
