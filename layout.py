from tkinter import *
import tkinter.ttk as ttk
import tkinter.filedialog, tkinter.messagebox
import getpass
import configparser
import sys

from PIL import Image, ImageTk  # in project requirements as 'Pillow'

import main

HEAD = ("Arial", 16)
FONT = ("Arial", 12)
COURIER = ("Courier New", 12)


class Window(Tk):

    def __init__(self, title, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.wm_resizable(0, 0)  # disables full screen and resizing
        self.title(title)
        self.wm_iconbitmap(".\images\doublehelix.ico")
        self.messages = ["Stop to stop running program then exit for quick exit.",  # File
                         "Edit the main form or reset both forms.",  # Edit
                         "Toggle the status bar.",  # View
                         "Edit the advanced menu."]  # Advanced

        self.container = Frame(self, bg='powder blue')

        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_columnconfigure(2, weight=1)

        side_bar = OptionsBar(self.container, self, bg='powder blue')
        side_bar.grid(column=0, rowspan=3, padx=(10, 0), pady=10)

        self.pb_space = Frame(self.container, bg='powder blue', height=22, width=400)
        self.pb_space.grid(row=7, columnspan=3)

        self.bar = ProgressWin(self.pb_space)

        self.status_bar = StatusBar(self.container)
        self.status_bar.grid(row=8, columnspan=3, sticky='ew', pady=(22, 0))
        self.status_bar.set("Ready")

        # ========
        # MENU BAR
        # ========

        self.menubar = Menu(self)

        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Stop", command=complete)
        filemenu.add_command(label="Exit", command=sys.exit)
        self.menubar.add_cascade(label="File", menu=filemenu)  # index = 0

        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Main Form",
                             command=lambda: self.show_frame('FormPage'))
        editmenu.add_separator()
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

        advancedmenu = Menu(self.menubar, tearoff=0)
        advancedmenu.add_command(label="Options", command=lambda: self.show_frame('AdvancedPage'))
        self.menubar.add_cascade(label="Advanced", menu=advancedmenu)  # index = 3

        self.config(menu=self.menubar)
        self.menubar.bind('<<MenuSelect>>', self.status_bar_update)

        # =================
        # NOTEBOOK AND TABS
        # =================

        self.nbk = ttk.Notebook(self.container, width=300, height=200)

        style = ttk.Style()
        style.configure('"My.TFrame', background='white')
        self.frames = {}  # contains ttk.Frame type for adding and showing frames
        self.custom_frames = {}  # contains custom types for accessing elements

        # AdvancedPage is before FormPage because FormPage init needs to access its methods (save and import_settings)
        for F in (StartPage, AdvancedPage, FormPage):
            frame = ttk.Frame(self.nbk)
            custom = F(frame, self, {'background': 'white',
                                     'borderwidth': '1',
                                     'relief': 'solid'})
            custom.pack(expand=1, fill=BOTH)
            custom.tkraise()
            self.frames[str(F)[15:-2]] = frame  # instead of the class as the key, the string of the class is the key
            self.custom_frames[str(F)[15:-2]] = custom

        self.nbk.grid(row=1, column=1, sticky='nsew', padx=(0, 20), pady=(20, 18))

        # ==========
        # POPUP MENU
        # ==========

        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label='Close', command=self.close_tab)
        self.popup.add_command(label='Open All Tabs', command=self.open_all_tabs)
        self.popup_index = None

        self.frame_indexes = {}
        self.current_frame = None
        self.add_frame('StartPage')

    def status_bar_toggle(self):
        if self.status_bar.label.winfo_ismapped():
            self.status_bar.grid_forget()
        else:
            self.status_bar.grid(row=8, columnspan=3, sticky='ew', pady=(41, 0))

    def status_bar_update(self, event=None):
        index = self.call(event.widget, "index", "active")
        if index in range(0, 4):
            self.status_bar.set(self.messages[index])
        else:
            self.status_bar.set("Ready")

    def show_frame(self, cont):
        if cont == 'AdvancedPage' and str(self.frames['FormPage']) not in self.nbk.tabs():
            tkinter.messagebox.showinfo(title='Unable to open advanced options',
                                        message='Please click New before accessing advanced options.')
        else:
            if str(self.frames[cont]) not in self.nbk.tabs():
                self.add_frame(cont)
            self.nbk.select(self.frame_indexes[cont])
            self.current_frame = cont

    def add_frame(self, cont):
        frame = self.frames[cont]  # shows the frame that is called by class
        self.nbk.add(frame, text=cont)
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
        if self.nbk.index('end') > 1 and self.popup_index is not None:  # if there is more than one tab open
            self.nbk.hide(self.popup_index)
            self.popup_index = None

    def open_all_tabs(self):
        tabs = ['StartPage', 'FormPage', 'AdvancedPage']
        for tab in tabs:
            self.show_frame(tab)

    def reset(self):
        self.custom_frames["FormPage"].v.set("Select file...")
        main.filename = None
        self.custom_frames["FormPage"].ents["Email"].delete(0, END)
        self.custom_frames["FormPage"].ents["Keywords"].delete(0, END)
        self.custom_frames["FormPage"].v2.set("Select file...")
        main.save_as_name = None

        self.custom_frames["AdvancedPage"].ents["Symbol Column"].delete(0, END)
        self.custom_frames["AdvancedPage"].ents["Symbol Column"].insert(0, 'G')
        self.custom_frames["AdvancedPage"].ents["Synonyms Column"].delete(0, END)
        self.custom_frames["AdvancedPage"].ents["Synonyms Column"].insert(0, 'H')
        self.custom_frames["AdvancedPage"].v.set("ALL")
        self.custom_frames["AdvancedPage"].entry.delete(0, END)
        self.custom_frames["AdvancedPage"].entry.config(state="disabled")
        self.custom_frames["AdvancedPage"].desc.set(0)
        self.custom_frames["AdvancedPage"].sort.set(0)


def complete():
    main.ask_quit = True


class StatusBar(Frame):

    def __init__(self, master):
        super().__init__(master)
        Frame.__init__(self, master)
        self.text = StringVar()
        self.label = Label(self,
                           anchor=W,
                           background="gray88",
                           textvariable=self.text,
                           foreground="dark slate gray")
        self.label.pack(fill=X)

    def set(self, status):
        self.text.set(status)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


class OptionsBar(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent)
        Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller

        image = Image.open(".\images\Information.png")
        image = image.resize((30, 30), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image)
        self.b1 = Label(self,
                        text="Info",
                        image=self.photo,
                        compound=TOP,
                        width=70,
                        bg='white',
                        cursor='hand2')
        self.b1.grid(row=0, padx=(20, 0), pady=15)
        self.b1.bind('<Button-1>', self.info_button)
        self.b1.bind('<Enter>', lambda e: self.b1.config(bg='light cyan'))
        self.b1.bind('<Leave>', lambda e: self.b1.config(bg='white'))
        self.b1.bind('<ButtonRelease-1>', lambda e: self.b1.config(bg='light cyan'))

        image2 = Image.open(".\images\Search.png")
        image2 = image2.resize((30, 30), Image.ANTIALIAS)
        self.photo2 = ImageTk.PhotoImage(image2)
        self.b2 = Label(self,
                        text="New",
                        image=self.photo2,
                        compound=TOP,
                        width=70,
                        bg='white',
                        cursor='hand2')
        self.b2.grid(row=1, padx=(20, 0), pady=15)
        self.b2.bind('<Button-1>', self.new_button)
        self.b2.bind('<Enter>', lambda e: self.b2.config(bg='light cyan'))
        self.b2.bind('<Leave>', lambda e: self.b2.config(bg='white'))
        self.b2.bind('<ButtonRelease-1>', lambda e: self.b2.config(bg='light cyan'))

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
        lab = Label(self, text="Info", font=HEAD, background="white")

        lab.grid(row=0, padx=120, pady=(40, 10))

        lab2 = Label(self, text="Visit -here- for more information", background="white")
        lab2.grid(row=1)


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
        self.popup.add_command(label='More Options', command=lambda: controller.show_frame('AdvancedPage'))

        self.popup.add_separator()
        self.popup.add_command(label='Import Settings',
                               command=controller.custom_frames['AdvancedPage'].import_settings)
        self.popup.add_command(label='Save Settings',
                               command=controller.custom_frames['AdvancedPage'].save)

        lab = Label(self, text="File: ", background='white')
        lab.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        b1 = ttk.Button(self, text="Browse...", command=self.askopenfilename)
        b1.grid(row=0, column=2, sticky=E, padx=5, pady=5)
        self.ents, make_form_widgets = make_form(self, ['Email', 'Keywords'])

        lab2 = Label(self, text="Save As: ", background='white')
        lab2.grid(row=3, column=0, sticky=W, padx=5, pady=5)

        b2 = ttk.Button(self, text="Browse...", command=self.asksaveasfilename)
        b2.grid(row=3, column=2, sticky=E, padx=5, pady=5)

        s = ttk.Style()
        s.configure('Blue.TLabel', background='LightBlue1')
        s.configure('White.TLabel', background='White')
        image = Image.open(".\images\\arrow-right.png")
        image = image.resize((30, 20), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image)
        self.b3 = ttk.Label(self, image=self.photo, style='White.TLabel')
        self.b3.grid(row=6, columnspan=3, padx=5, pady=(20, 5))
        self.b3.bind('<Button-1>', lambda e: main.get_entries(controller))
        self.b3.bind('<Enter>', lambda e: self.b3.config(style='Blue.TLabel'))
        self.b3.bind('<Leave>', lambda e: self.b3.config(style='White.TLabel'))

        self.v = StringVar()
        self.v.set("Select file...")
        lab3 = Label(self, textvariable=self.v, background="white")
        lab3.grid(row=0, column=1, padx=5, pady=5)

        self.v2 = StringVar()
        self.v2.set("Select file...")
        lab4 = Label(self, textvariable=self.v2, background="white")
        lab4.grid(row=3, column=1, padx=5, pady=5)

        make_form_widgets.extend([self, lab, lab2, lab3, lab4, self.b3])
        widgets = make_form_widgets

        add_tag('form_elements', widgets)  # TODO include the make_form elements
        self.bind_class('form_elements', '<Button-3>', self.on_button_3)

    def askopenfilename(self):
        file = tkinter.filedialog.askopenfilename(**self.file_opt)
        if file:
            f_display = file.split('/')[-1]
            main.filename = file
            self.v.set(f_display)

    def asksaveasfilename(self):
        file = tkinter.filedialog.asksaveasfile(**self.file_opt)
        if file:
            s_display = file.name.split('/')[-1]
            main.save_as_name = file.name
            self.v2.set(s_display)

    def on_button_3(self, event):
        try:
            self.popup.tk_popup(event.x_root + 60, event.y_root + 11, 0)
        finally:
            self.popup.grab_release()


class AdvancedPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent,  *args, **kwargs)
        # Frame.__init__(parent, *args, **kwargs)
        self.controller = controller
        self.ents, _ = make_form(self, ["Symbol Column", "Synonyms Column"])

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.ents["Symbol Column"].insert(0, 'G')
        self.ents["Synonyms Column"].insert(0, 'H')

        s = ttk.Style()
        s.configure("White.TRadiobutton", background="white")
        s.configure("White.TCheckbutton", background="white")

        lab = Label(self, text="Number of Genes to Use:", background="white")
        lab.grid(row=3, columnspan=3, sticky=W, padx=5, pady=(10, 0))

        self.v = StringVar()
        self.v.set("ALL")
        rb = ttk.Radiobutton(self, text="All", variable=self.v, value="ALL", command=self.disable_entry,
                             style="White.TRadiobutton")
        rb2 = ttk.Radiobutton(self, text="Top x genes", variable=self.v, value="SELECT", command=self.enable_entry,
                              style="White.TRadiobutton")
        self.entry = ttk.Entry(self, width=10, state="disabled", style="EntryStyle.TEntry")
        self.entry.bind("<Button-1>", self.entry_click)

        rb.grid(row=4, column=0, sticky=W, padx=5, pady=5)
        rb2.grid(row=4, column=1, sticky=E, padx=5, pady=5)
        self.entry.grid(row=4, column=2, sticky=W, pady=5)

        self.desc = IntVar()  # if desc is 1, then it is checked
        self.sort = IntVar()  # if sort is 1, then it is checked

        c = ttk.Checkbutton(self, text="Add descriptions", variable=self.desc, style="White.TCheckbutton")
        c.grid(row=5, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        c2 = ttk.Checkbutton(self, text="Sort", variable=self.sort, style="White.TCheckbutton")
        c2.grid(row=5, column=2, sticky=W, padx=5, pady=5)

        b1 = ttk.Button(self, text="Import Settings", command=self.import_settings)
        b1.grid(row=6, column=0, padx=5, pady=5)

        b2 = ttk.Button(self, text="Back",
                    command=lambda: self.controller.show_frame("FormPage"))
        b2.grid(row=6, column=2, padx=5, pady=5)
        b3 = ttk.Button(self, text="Save Settings", command=self.save)
        b3.grid(row=6, column=1, padx=5, pady=5)

        self.ents["Symbol Column"].focus_set()

    def entry_click(self, _):
        self.v.set("SELECT")
        self.enable_entry()

    def enable_entry(self):
        self.entry.configure(state="normal")
        self.entry.update()

    def disable_entry(self):
        self.entry.configure(state="disabled")
        self.entry.update()

    def save(self):
        if not self.config.has_section("main"):
            self.config.add_section("main")
        if not self.config.has_section("advanced"):
            self.config.add_section("advanced")

        self.config.set("advanced", "Symbol Column", self.ents["Symbol Column"].get())
        self.config.set("advanced", "Synonyms Column", self.ents["Synonyms Column"].get())
        self.config.set("advanced", "Genes to Use", "ALL" if self.v.get()=="ALL" else self.entry.get())
        self.config.set("advanced", "Descriptions", str(self.desc.get()))
        self.config.set("advanced", "Sort", str(self.sort.get()))

        self.config.set("main", "Filename", '' if main.filename is None else main.filename)
        self.config.set("main", "Email", self.controller.custom_frames["FormPage"].ents["Email"].get())
        self.config.set("main", "Keywords", self.controller.custom_frames["FormPage"].ents["Keywords"].get())
        self.config.set("main", "Save As", '' if main.save_as_name is None else main.save_as_name)

        with open("config.ini", "w") as f:
            self.config.write(f)
        tkinter.messagebox.showinfo(title='Success',
                                    message='Your options have been saved. Import settings for future use.')

    def import_settings(self):
        try:
            self.ents["Symbol Column"].delete(0, END)
            self.ents["Synonyms Column"].delete(0, END)
            self.ents["Symbol Column"].insert(0, self.config.get("advanced", "Symbol Column"))
            self.ents["Synonyms Column"].insert(0, self.config.get("advanced", "Synonyms Column"))
            if self.config.get("advanced", "Genes to Use") == "ALL":
                self.v.set("ALL")
            else:
                self.v.set("SELECT")
                self.entry.config(state="normal")
                self.entry.delete(0, END)
                self.entry.insert(0, self.config.get("advanced", "Genes to Use"))
            self.desc.set(int(self.config.get("advanced", "Descriptions")))
            self.sort.set(int(self.config.get("advanced", "Sort")))

            main.filename = self.config.get("main", "Filename") if self.config.get("main", "Filename") != '' else None
            self.controller.custom_frames["FormPage"].v.set("Select file..." if self.config.get("main", "Save As") == '' else
                                                            self.config.get("main", "Filename").split('/')[-1])
            self.controller.custom_frames["FormPage"].ents["Email"].delete(0, END)
            self.controller.custom_frames["FormPage"].ents["Email"].insert(0, self.config.get("main", "Email"))
            self.controller.custom_frames["FormPage"].ents["Keywords"].delete(0, END)
            self.controller.custom_frames["FormPage"].ents["Keywords"].insert(0, self.config.get("main", "Keywords"))
            main.save_as_name = self.config.get("main", "Save As") if self.config.get("main", "Save As") != '' else None
            self.controller.custom_frames["FormPage"].v2.set("Select file..." if self.config.get("main", "Save As") == '' else
                                                            self.config.get("main", "Save As").split('/')[-1])

        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            tkinter.messagebox.showerror(title="Outdated config.ini",
                                         message="Config.ini file is invalid or outdated, please save settings again. "
                                         + str(e))


class ProgressWin(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pb = ttk.Progressbar(parent, orient='horizontal', length=400, mode='determinate')
        # self.pb.grid(columnspan=2, padx=5)

        self.items = 0  # number of queries searched so far
        self.total_items = 0  # the total number of queries to be searched

    def start(self):  # inc is the number of keywords, which the progress bar will update by
        self.pb['value'] = 0
        self.pb['maximum'] = main.total_queries
        self.load()

    def load(self):
        self.items = main.pb_int
        self.pb['value'] = self.items
        if self.items < main.total_queries:
            self.after(1000, self.load)  # updates after 1 second


def make_form(frame, fields):
    entries = {}
    widgets = []
    n = 1
    for field in fields:
        row = Frame(frame)
        lab = Label(row, width=22, text=field+": ", anchor='w', background="white")
        ent = ttk.Entry(row, style="Thistle.TEntry")
        row.grid(row=n, column=0, columnspan=3, padx=5, pady=5)
        lab.grid(row=n, column=1, sticky=E)
        ent.grid(row=n, column=2, sticky="nsew")

        widgets.extend([row, lab, ent])
        entries[field] = ent
        n += 1
    return entries, widgets


def add_tag(tag, args):
    """Adds the tag parameter as a bind tag for the other parameters (widgets)"""
    for widget in args:
        widget.bindtags((tag,) + widget.bindtags())
