from tkinter import *
from tkinter.ttk import *
import tkinter.filedialog, tkinter.messagebox
import getpass
import configparser
import os

import main

HEAD = ("Arial", 16)
FONT = ("Arial", 12)
COURIER = ("Courier New", 12)


class Window(Tk):

    def __init__(self, title, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title(title)
        self.wm_iconbitmap("doublehelix.ico")

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(2, weight=1)

        self.frames = {}

        for F in (StartPage, FormPage, SuccessPage, AdvancedPage):
            frame = F(container, self)
            self.frames[str(F)[15:-2]] = frame  # instead of the class as the key, the string of the class is the key
            frame.grid(row=1, column=1, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, cont):
        frame = self.frames[cont]  # shows the frame that is called by class
        frame.tkraise()
        self.current_frame = cont

    def reset(self):
        self.frames["FormPage"].v.set("Select file...")
        main.filename = None
        self.frames["FormPage"].ents["Email"].delete(0, END)
        self.frames["FormPage"].ents["Keywords"].delete(0, END)
        self.frames["FormPage"].v2.set("Select file...")
        main.save_as_name = None

        self.frames["AdvancedPage"].ents["Symbol Column"].delete(0, END)
        self.frames["AdvancedPage"].ents["Symbol Column"].insert(0, 'G')
        self.frames["AdvancedPage"].ents["Synonyms Column"].delete(0, END)
        self.frames["AdvancedPage"].ents["Synonyms Column"].insert(0, 'H')
        self.frames["AdvancedPage"].v.set("ALL")
        self.frames["AdvancedPage"].entry.delete(0, END)
        self.frames["AdvancedPage"].entry.config(state="disabled")
        self.frames["AdvancedPage"].desc.set(0)
        self.frames["AdvancedPage"].sort.set(0)

    def menu_config(self):
        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Stop", command=self.complete_quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Main Form",
                             command=lambda: self.show_frame("FormPage"))
        editmenu.add_separator()
        editmenu.add_command(label="Reset", command=self.reset)
        menubar.add_cascade(label="Edit", menu=editmenu)

        advancedmenu = Menu(menubar, tearoff=0)
        advancedmenu.add_command(label="Options", command=self.options_go)
        # TODO if the frame is already "AdvancedPage," then it should go to "FormPage"

        menubar.add_cascade(label="Advanced", menu=advancedmenu)

        self.config(menu=menubar)

    def complete_quit(self):
        main.ask_quit = True

    def options_go(self):
        if self.current_frame == "AdvancedPage":
            self.show_frame("FormPage")
        else:
            self.show_frame("AdvancedPage")


class StartPage(Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        Frame.__init__(self, parent)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        label = Label(self, text="BioDataSorter", font=HEAD)
        label.grid(row=0)
        b1 = Button(self, text="Begin",
                    command=self.start)
        b1.grid(row=2, pady=10)

    def start(self):
        self.controller.show_frame("FormPage")
        self.controller.menu_config()



class FormPage(Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.file_opt = options = {}
        options['defaultextension'] = '.xlsx'
        options['filetypes'] = [('excel files', '.xlsx')]
        options['initialdir'] = 'C:\\Users\\%s\\' % getpass.getuser()
        options['parent'] = controller
        options['title'] = 'Choose a file'

        lab = Label(self, text="File: ")
        lab.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        b1 = Button(self, text="Browse...", command=self.askopenfilename)
        b1.grid(row=0, column=2, sticky=E, padx=5, pady=5)
        self.ents = main.make_form(self, ["Email", "Keywords"])
        lab2 = Label(self, text="Save As: ")
        lab2.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        b2 = Button(self, text="Browse...", command=self.asksaveasfilename)
        b2.grid(row=3, column=2, sticky=E, padx=5, pady=5)
        self.b3 = Button(self, text="Next", width=5, command=lambda: main.get_entries(controller))
        self.b3.grid(row=6, columnspan=3, padx=5, pady=(20,5))

        self.v = StringVar()
        self.v.set("Select file...")
        lab3 = Label(self, textvariable=self.v)
        lab3.grid(row=0, column=1, padx=5, pady=5)

        self.v2 = StringVar()
        self.v2.set("Select file...")
        lab4 = Label(self, textvariable=self.v2)
        lab4.grid(row=3, column=1, padx=5, pady=5)

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


class AdvancedPage(Frame):
    # TODO add choice for sort and number of genes to extract from file

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.ents = main.make_form(self, ["Symbol Column", "Synonyms Column"])

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.ents["Symbol Column"].insert(0, 'G')
        self.ents["Synonyms Column"].insert(0, 'H')

        lab = Label(self, text="Number of Genes to Use:")
        lab.grid(row=3, columnspan=3, sticky=W, padx=5, pady=(10, 0))

        self.v = StringVar()
        self.v.set("ALL")
        rb = Radiobutton(self, text="All", variable=self.v, value="ALL", command=self.disable_entry)
        rb2 = Radiobutton(self, text="Top x genes", variable=self.v, value="SELECT", command=self.enable_entry)
        self.entry = Entry(self, width=10, state="disabled")
        rb.grid(row=4, column=0, sticky=W, padx=5, pady=5)
        rb2.grid(row=4, column=1, sticky=E, padx=5, pady=5)
        self.entry.grid(row=4, column=2, sticky=W, pady=5)

        self.desc = IntVar()  # if desc is 1, then it is checked
        self.sort = IntVar()  # if sort is 1, then it is checked

        c = Checkbutton(self, text="Add descriptions", variable=self.desc)
        c.grid(row=5, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        c2 = Checkbutton(self, text="Sort", variable=self.sort)
        c2.grid(row=5, column=2, sticky=W, padx=5, pady=5)

        b1 = Button(self, text="Import Settings", command=self.import_settings)
        b1.grid(row=6, column=0, padx=5, pady=5)

        b2 = Button(self, text="Back",
                    command=lambda: self.controller.show_frame("FormPage"))
        b2.grid(row=6, column=2, padx=5, pady=5)
        b3 = Button(self, text="Save Settings", command=self.save)
        b3.grid(row=6, column=1, padx=5, pady=5)

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
        self.config.set("main", "Email", self.controller.frames["FormPage"].ents["Email"].get())
        self.config.set("main", "Keywords", self.controller.frames["FormPage"].ents["Keywords"].get())
        self.config.set("main", "Save As", '' if main.save_as_name is None else main.save_as_name)

        with open("config.ini", "w") as f:
            self.config.write(f)
        self.controller.show_frame("FormPage")

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
            self.desc.set(self.config.get("advanced", "Descriptions"))
            self.desc.set(self.config.get("advanced", "Sort"))

            main.filename = self.config.get("main", "Filename") if self.config.get("main", "Filename") != '' else None
            self.controller.frames["FormPage"].v.set("Select file..." if self.config.get("main", "Save As") == '' else \
                                                         self.config.get("main", "Filename").split('/')[-1])
            self.controller.frames["FormPage"].ents["Email"].delete(0, END)
            self.controller.frames["FormPage"].ents["Email"].insert(0, self.config.get("main", "Email"))
            self.controller.frames["FormPage"].ents["Keywords"].delete(0, END)
            self.controller.frames["FormPage"].ents["Keywords"].insert(0, self.config.get("main", "Keywords"))
            main.save_as_name = self.config.get("main", "Save As") if self.config.get("main", "Save As") != '' else None
            self.controller.frames["FormPage"].v2.set("Select file..." if self.config.get("main", "Save As") == '' else\
                                                          self.config.get("main", "Save As").split('/')[-1])

        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            tkinter.messagebox.showerror(title="Outdated config.ini",
                                         message="Config.ini file is invalid or outdated, please save settings again. "
                                         + str(e))


class SuccessPage(Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        Frame.__init__(self, parent)
        self.v = StringVar()
        lab1 = Label(self, textvar=self.v)
        lab1.grid(row=0)

    def set_string(self):
        self.v.set("Your file is located in " + os.path.dirname(main.filename))


class ProgressWin(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pb = Progressbar(self, orient="horizontal", length=parent.controller.winfo_width()-40, mode="determinate")
        self.pb.grid(column=4, padx=5, pady=10)

        self.items = 0  # number of queries searched so far
        self.total_items = 0  # the total number of queries to be searched

    def start(self):  # inc is the number of keywords, which the progress bar will update by
        self.pb["value"] = 0
        self.pb["maximum"] = main.total_queries
        self.load()

    def load(self):
        self.items = main.pb_int
        self.pb["value"] = self.items
        if self.items < main.total_queries:
            self.after(1000, self.load)

