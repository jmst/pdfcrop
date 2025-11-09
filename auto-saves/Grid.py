import start
import tkinter as tk
from tkinter import ttk

from pathlib import Path

class Form():
    def __init__(self, master, label, button_label, default):
        label = ttk.Label(master, text=label + ': ')
        label.grid(column=0, row=0)
        
        self.txtvar = tk.StringVar(master, default) # need to maintain reference? self or root
        entry = ttk.Entry(master, textvariable = self.txtvar)
        entry.grid(column=1, row=0, sticky=tk.EW)
        # entry.configure(state = tk.DISABLED)

        fn_button = ttk.Button(master, text = button_label, width = 0)
        fn_button.grid(column=2, row=0, sticky=tk.E)

        # master.columnconfigure(0, weight=0)
        # master.columnconfigure(1, weight=1)
        # master.columnconfigure(2, weight=0)


class Widgets():
    def __init__(self, root):
        grid = Grid(root)
        
        filename = "C:/Users/James/Desktop/projects/code/py/pdfcrop/houdini_foundations_19_5_01.pdf"
        fn_entry = Form(grid.north, 'File', 'Open', filename)

        crop_btn = ttk.Button(grid.west, text='Crop') #, command = crop_btn_event)
        crop_btn.grid(row=1, sticky='n')
        
        out_form = Form(grid.south, 'Output', 'Crop', Path(filename).name + '_cropped.pdf')

class Grid():
    def __init__(self, root):
        # Top-level Frame
        self.main=ttk.Frame(root)
        self.main.grid(sticky=tk.NSEW)
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=0)
        self.main.rowconfigure(0, weight=0)
        self.main.rowconfigure(1, weight=1)

        # North - Filename of input entry
        self.north=ttk.Frame(self.main, borderwidth=1)
        self.north.grid(row=0, sticky=tk.EW, columnspan=2)
        self.north.columnconfigure(0, weight=0)
        self.north.columnconfigure(1, weight=1)
        self.north.rowconfigure(1, weight=0)

        # West - Guideline value spinboxes and minimap
        self.west=ttk.Frame(self.main, borderwidth=20, relief="ridge")
        self.west.grid(column=0, row=1, ipadx="5", sticky=tk.NSEW)
        self.west.columnconfigure(0, weight=1)
        self.west.rowconfigure(0, weight=1)
        self.west.rowconfigure(1, weight=1)

        self.input_frame=ttk.Frame(self.west)#, width=30, height=10)
        self.input_frame.grid(row=0, sticky=tk.S)

        minimap=ttk.Frame(self.west) # height=100
        minimap.grid(column=0, row=2, sticky=tk.NSEW)

        ## East - Image Canvas with mouse interactive guidelines
        # todo can't set as self.frame_east? horseshit
        self.east=ttk.Frame(self.main)
        self.east.grid(column=1, row=1, sticky=tk.NSEW)
        

        self.south = ttk.Frame(self.main)
        self.south.grid(column=0, row=2)
        self.south.columnconfigure(0, weight=0)
        self.south.columnconfigure(1, weight=1)
        self.south.columnconfigure(2, weight=0)
        
if __name__ == '__main__':    
    def grid(root):
        grid = Grid(root)
        # grid.east.configure(width = 100)
        # grid.main.configure(width = 1000)
        conf(root.winfo_children()[0])

    def form(root):
        Form(root, "File: ", "Open", "test")
        conf(root)

    def conf(parent: tk.Tk):
        ttk.Style().configure("magenta.TFrame", background='magenta')
        ttk.Style().configure("black.TFrame", background='black')
        ttk.Style().configure("magenta.TLabel", background='magenta', foreground = 'black')
        ttk.Style().configure("black.TLabel", background='black', foreground = 'white')
        parent.winfo_toplevel().geometry('300x300')
        def span(s, frame: ttk.Frame):
            # child.grid_configure(sticky = tk.NSEW)
            for i in range(s):
                frame.columnconfigure(i, weight=1)
                frame.rowconfigure(i, weight=1)            
            return '+' + str(s) if (s := int(s) - 1) > 0 else ''
        def grid_opts(parent, bg):
            for child in parent.winfo_children():
                if child.winfo_class() == 'TFrame':
                    def s(bg): return 'magenta' if bg else 'black'
                    child.configure(style = s(bg) + ".TFrame")
                    # if not child.cget('borderwidth'):
                    child.configure(borderwidth = 2, relief = 'ridge')
                    
                    g = child.grid_info()
                    txt = f"({g['column']}{span(g['columnspan'], child)}," \
                        + f"{g['row']}{span(g['rowspan'], child)})"
                    label = ttk.Label(child, text=txt, style = s(bg) + '.TLabel')
                    label.grid(column=0, row=0)

                    grid_opts(child, not bg)

        grid_opts(parent, True)

    start.start(grid)
    # start.start(form)
    # start.start(Widgets)
