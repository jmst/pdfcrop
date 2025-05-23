import os

import start

import tkinter as tk
from tkinter import ttk

# from PIL import Image

from pathlib import Path

from Panels import MenuBar, LineSpinBox
from pdfcanvas import PdfCanvas
import Grid

class TkGui:
    """Main GUI class."""
    frame_east: ttk.Frame

    def __init__(self, root):
        """Geometry and methods"""
        
        progname = "pdfcrop"
        self.filename = tk.StringVar(root)
        def set_title(strvar):
            name = Path(root.getvar(strvar)).name
            root.title(name + "  -  " + progname if name else progname)
        self.filename.trace_add("write", lambda strvar, *_: set_title(strvar))
        # self.filename.trace_add("unset", lambda *_: root.title("deleted")) # for when active file deleted?

        self.filename.set("C:/Users/James/Desktop/projects/code/py/pdfcrop/houdini_foundations_19_5_01.pdf")

        # self.progname = root.title

        #? self.controlidx = 0

        grid = Grid.Grid(root)
        
        self.pdfcanvas = PdfCanvas(root, grid.east)

        self.pdfcanvas.open(self.filename.get())
        img = self.pdfcanvas.img
        lines = self.pdfcanvas.canvaslines
        self.line_matrix = lines.line_matrix

        LineSpinBox(grid.input_frame, self.line_matrix, img['sample'], lines,
                                    lines.pref_pixel_ref)
        
        self.menubar = MenuBar(root)
        
        # crop_btn.bind('<Button-1>', self.crop_btn_event)

    def crop_btn_event(self): # , _event):
        coords = []
        for ln in self.line_matrix:
            lm = self.line_matrix[ln]
            coords.append(lm['unconv'].get()/2)
        print(coords)
        y0, yoff, x0, xoff = coords
        print(coords)
        # for ln in self.line_matrix:
        #     lm = self.line_matrix[ln]
        #     lm['unconv'].set(self.unconv(lm['pos'].get(), lm))
        # print(self.line_matrix)
        dir = os.getcwd()
        i_file = Path(dir, "houdini_foundations_19_5_01.pdf")
        o_file = i_file.with_stem(i_file.stem + "_cropped_gui")
        doc = pymupdf.open(i_file)
        for i in range (1, 226):
            print("Cropping", i)
            page = doc[i-1]
            x1 = page.rect.x1
            print(x1)
            y1 = page.rect.y1
            print(y1)
            # if (i % 2 != 0):
            #     x0, xoff = xoff, x0
            page.set_cropbox(pymupdf.Rect(x0, y0, xoff, yoff)) #x1y1
        doc.save(os.path.join(o_file))
        

    # def addLabel(self, txt):
    #     ttk.Label(mainframe, text=txt, background="red"
    #               ).grid(column=0, row=self.controlidx)
    #     self.controlidx += 1

if __name__ == "__main__":
    start.start(TkGui)
