import pymupdf
import os

from ctypes import windll

import tkinter as tk
from tkinter import ttk

# from PIL import Image

from pathlib import Path

from Panels import MenuBar, PdfCanvas, CanvasLines, LineSpinBox

class TkGui:
    """Main GUI class."""
    frame_east: ttk.Frame

    def __init__(self, root):
        """Geometry and methods"""

        #? self.controlidx = 0
        debugc = 'magenta'
        debugc2 = 'black'
        
        # def init_frames(root):
        ttk.Style().configure("debug-bg.TFrame", background=debugc)
        ttk.Style().configure("debug-fg.TFrame", background=debugc2)

        # Top-level Frame
        frame_main=ttk.Frame(root)
        frame_main.grid(sticky='NSEW')
        frame_main.columnconfigure(0, weight=1)
        frame_main.columnconfigure(1, weight=0)
        frame_main.rowconfigure(0, weight=0)
        frame_main.rowconfigure(1, weight=1)

        # North - Filename of input entry
        frame_north=ttk.Frame(frame_main, borderwidth=1)
        frame_north.grid(row=0, sticky="we", columnspan=2)
        frame_north.columnconfigure(0, weight=0)
        frame_north.columnconfigure(1, weight=1)
        frame_north.rowconfigure(1, weight=0)

        fn_label = ttk.Label(frame_north, text="File: ")
        fn_label.grid(column=0, row=0)
        fn_entry = ttk.Entry(frame_north)
        fn_entry.grid(column=1, row=0, sticky="we")

        # West - Guideline value spinboxes and minimap
        frame_west=ttk.Frame(frame_main, borderwidth=20, relief="ridge")
        frame_west.grid(column=0, row=1, ipadx="5", sticky='NSEW')

        frame_west.columnconfigure(0, weight=1)
        frame_west.rowconfigure(0, weight=1)
        frame_west.rowconfigure(1, weight=1)

        input_frame=ttk.Frame(frame_west, width=30, height=10)
        input_frame.grid(row=0, sticky='s')

        crop_btn = ttk.Button(frame_west, text='Crop', command = self.crop_btn_event)
        crop_btn.grid(row=1, sticky='n')

        minimap=ttk.Frame(frame_west, height=100, style="debug-fg.TFrame")
        minimap.grid(column=0, row=2, sticky='NSEW')

        ## East - Image Canvas with mouse interactive guidelines
        # todo can't set as self.frame_east? horseshit
        frame_east=ttk.Frame(frame_main)
        frame_east.grid(column=1, row=1, sticky='n')

        # (im_scrollh, im_scrollv, im_scrollbut, # subframe_image,
        # return input_frame, crop_btn, self.frame_east

            # def make_line_set(**kwargs):
            #     set = {}
            #     for ln in list(line_matrix):
            #         line = self.canvas.create_line(line_matrix[ln]['coords'], **kwargs)
            #         set[ln] = {'canv': line}
            #         match ln[0]:
            #             case 'h':
            #                 set[ln]['direction'] = 'y'
            #             case 'v':
            #                 set[ln]['direction'] = 'x'
            #     return set

            # _init to check if closest to og pos ie. canvas edge
            # TODO make this optional; og pos != canvas edge circumstance?
            # could show in debug mode # line_set_init = make_line_set(state='hidden')
            # self.line_set = make_line_set(width=debug_lt, fill='red')

            # line_set_length = len(self.line_set)
            # line_set_length = len(line_matrix)

            # global/instance so reusable for <B1-Motion> callback
            # self.line_index = 'h0' # req. init value if spinbox used first, fix todo
            # self.line_direction = 'x' # str, again req. ^^

            # print(self.line_set)

            # for line in list(self.line_set):
            #     self.line_set[line]['txtvar'] = DoubleVar(root)

            # print(self.line_set)
            # initialises line_set txtvars
            # def hvset(line):
            #     match self.line_set[line]['direction']: # 0=x0, 1=y0
            #         case 'y':
            #             xy = 1
            #         case 'x':
            #             xy = 0
            #         case _:
            #             raise Exception("Line not in line_set")                
            #     self.line_set[line]['txtvar'].set(
            #         self.canvas.coords(line_matrix[line]['coords'])[xy])

            # for line in list(self.line_set):
            #     hvset(line)

            # return line_matrix

        root.title("pdfcrop")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # im_frame, im_scrollh, im_scrollv, im_scrollbut, \
        # input_frame, crop_btn, frame_east = init_frames(root)
        # self.canvas, self.pdf_item = init_canvas(self.lt)
        self.pdfcanvas = PdfCanvas(root, frame_east)
        self.pdfcanvas.a_size(5)
        self.active_img = self.pdfcanvas.set_image('t-0.png')
        self.img = self.pdfcanvas.images[self.active_img]

        self.pdfcanvas.im_scrollbut['command'] = lambda: self.pdfcanvas.image_scale(
            root, self.img, 0)

        canvaslines = CanvasLines(root, self.pdfcanvas.canvas, self.img) # todo .line_matrix
        self.line_matrix = canvaslines.line_matrix #  self.pdfcanvas.init_lines(self.lt)

        # init_spinboxes()
        LineSpinBox(self.line_matrix, input_frame, self.img['sample'],
                                    canvaslines.pref_pixel_ref, canvaslines)
        
        # init_menu()
        self.menubar = MenuBar(root)
        
        # root.resizable(FALSE, FALSE)

        # root.attributes('-topmost', 1)
        # print(root.tk.eval('wm stackorder '+str(root)))

        # binds

        self.pdfcanvas.im_scrollbut.bind('<Button-2>', lambda e:
                          self.pdfcanvas.canvas.itemconfigure(self.pdfcanvas.raster, image=self.img['og']))
        self.pdfcanvas.im_scrollbut.bind('<Button-3>', lambda e: self.pdfcanvas.a_size(5))
        self.pdfcanvas.canvas.bind('<Button-1>', canvaslines.get_line)
        self.pdfcanvas.canvas.bind('<B1-Motion>', canvaslines.move_line_mevent)
        # crop_btn.bind('<Button-1>', self.crop_btn_event)

    def crop_btn_event(self): # , _event):
        coords = []
        for ln in self.line_matrix:
            lm = self.line_matrix[ln]
            coords.append(lm['unconv'].get())
        x0, xoff, y0, yoff = coords
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
    windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    TkGui(root)
    root.mainloop()
 
# if __name__ == "__main__":
#     import asyncio
#     import logging
    
#     # LOGGING.basicConfig(level=logging.DEBUG)
#     # logging.getLogger("asyncio").setLevel(logging.WARNING)
#     windll.shcore.SetProcessDpiAwareness(2)
#     root = Tk()
#     gui = TkGui(root)

#     async def async_input():
#         loop = asyncio.get_running_loop()
#         await loop.run_in_executor(
#             None, input)
#     async def updater():
#         while True:
#             root.update()
#             await asyncio.sleep(0.2)
#             await asyncio.async_input()

#     asyncio.run(updater(), debug=True)
