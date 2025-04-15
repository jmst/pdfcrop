import sys
import pymupdf
import os

from ctypes import windll

from _tkinter import TclError
from tkinter import (Tk, StringVar, IntVar, DoubleVar, Event,
                     Menu, Canvas, PhotoImage, Frame,
                     NORMAL, DISABLED, TRUE, FALSE)
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.ttk import Button
# existing ttk.Widgets will still work as named ttk., so replace them
# existing tk.Frame options fail # from tkinter.ttk import Frame
from math import ceil, floor
# from PIL import Image
from formula import a_sizer

from pathlib import Path

class MenuBar:
    # self not necessary?
    def __init__(self, root):
        root.option_add('*tearOff', False)
        menubar = Menu(root)
        root['menu'] = menubar
        menu_file = Menu(root)
        menubar.add_cascade(label='File', menu=menu_file)
        menu_file.add_command(label='Open...', command = fd.askopenfilename)
        menu_file.add_command(label='Save', command = lambda: print('save PLACEHOLDER'))
        menu_file.add_command(label='Save As...', command = fd.asksaveasfilename)
        menu_edit = Menu(root)
        menubar.add_cascade(label='Edit', menu=menu_edit)
        menu_edit.add_command(label='Preset 1')
        menu_edit.add_command(label='A5')
        menu_view = Menu(root)
        menubar.add_cascade(label='View', menu=menu_view)
        menu_view.add_command(label='Portrait/Landscape')
        menu_help = Menu(root)
        menubar.add_cascade(label='Help', menu=menu_help)
        menu_help.add_command(label='Github')
        menu_help.add_command(label='email@test')
        menu_help.entryconfigure('email@test', state=DISABLED) # copy symbol

class TkGui:
    """Main GUI class."""
    
    def __init__(self, root):
        """Geometry and methods"""
        def init_frames(root):
            ttk.Style().configure("debug-bg.TFrame", background=debugc)
            ttk.Style().configure("debug-fg.TFrame", background=debugc2)

            image_subframe_borderwidth = 10

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
            frame_east=ttk.Frame(frame_main)
            frame_east.grid(column=1, row=1, sticky='n')

            subframe_scrollbut=ttk.Frame(frame_east)#tk., bd=1, bg=debugc)
            subframe_scrollbut.grid_propagate(False)
            subframe_scrollbut.grid(column=1, row=0, sticky='NSEW')
            subframe_scrollbut.columnconfigure(0, weight=1)
            subframe_scrollbut.rowconfigure(0, weight=1)

            subframe_image=Frame(frame_east, relief='sunken', bd=image_subframe_borderwidth)
            subframe_image.grid(column=0, row=1)
            subframe_image.columnconfigure(0, weight=1)
            subframe_image.rowconfigure(0, weight=1)
            
            im_scrollh=ttk.Scrollbar(frame_east, orient='horizontal')
            im_scrollh.grid(column=0, row=0, sticky='we')
            
            im_scrollv=ttk.Scrollbar(frame_east, orient='vertical')
            im_scrollv.grid(column=1, row=1, sticky='ns')
            
            im_scrollbut=Button(subframe_scrollbut)
            im_scrollbut.grid()

            return (subframe_image, im_scrollh, im_scrollv, im_scrollbut,
                    input_frame, crop_btn)

        def conv(i, line):
            i = (i / self.img['sample']
                 + self.line_matrix[line]['conv'])
            return i

        # ! must call after init self.canvas
        def canvas_a_size(a_size): # A-series paper size eg. A4
            # TODO other standard print sizes eg. US
            # not used once imaged resized
            width, height = a_sizer(a_size)
            self.canvas['width']=str(width + self.lt)+'m'
            self.canvas['height']=str(height + self.lt)+'m'

        def init_canvas(lt):            
                canvas=Canvas(im_frame,
                    highlightthickness = 0,
                    highlightcolor = 'white',
                    bg='grey',
                    xscrollcommand=im_scrollh.set,
                    yscrollcommand=im_scrollv.set)
                       # scrollregion=(0,0,width,height))
                # im_scrollh['command']=canvas.xview
                # im_scrollv['command']=canvas.yview
                # print(self.im_canvas['highlightthickness'])
                canvas.grid(sticky='NSEW')

                # anchor nw for guillotine metaphor (todo opt)
                pdf_item = canvas.create_image(lt, lt, anchor='nw')

                return canvas, pdf_item
            
        def init_image(filename):
            i_file = Path(filename)
            name = i_file.stem
            # todo hc mode opt to use bitmap (like pdf.js)
            ogpdf = PhotoImage(master=root, file=filename) # master=self.im_canvas
            
            # calc nearest integer scaling to fit canvas
            subx = (float(self.canvas['width'])  + self.lt) / ogpdf.width()
            suby = (float(self.canvas['height']) + self.lt) / ogpdf.height()
            sample = ceil(1/min(subx, suby))

            self.images[name] = {'og': ogpdf, 'path': filename, 'sample': sample}
            self.image_scale(root, self.images[name], 0)

            # print(float(self.canvas['height']))
            self.canvas_fit(self.images[name]['scaled'])
            # print(float(self.canvas['height']))
            # self.image_scale(root, ogpdf, 3)
            return name

        def init_lines(lt):
            
            debug_lt = lt
            lineo = lt//2 #-(lt%2)
            pdf = self.img['scaled']
            xe = pdf.width()  + lt * 2
            ye = pdf.height() + lt * 2

            # NSEW unsorted list() order matters for self.move_line
            line_matrix = {}
            for ln in ['h0', 'h1', 'v0', 'v1']:
                lm = line_matrix[ln] = {}
                p = IntVar(root) # type check in get_coords
                lm['pos'] = p
                dim = 0
                match ln[0]:
                    case 'h':
                        dim = pdf.height() # ? make var for spinbox limit access
                        lm['coords'] = [0, p, xe, p]
                        lm['limit'] = ye - lineo - 1
                    case 'v':
                        dim = pdf.width()
                        lm['coords'] = [p, 0, p, ye]
                        lm['limit'] = xe - lineo - 1 # todo can use ogpos instead
                match ln[1]:
                    case '0':
                        val = lm['conv'] = lineo
                        p.set(val)
                    case '1':
                        # line width pad + entire left border (line thickness)
                        # simpler as 3x lineo + 1 (line centre)?
                        lm['conv'] = lineo + lt
                        val = dim + lm['conv']
                        p.set(val)
                lm['ogpos'] = p.get()
                lm['unconv'] = IntVar(root, self.unconv(lm['pos'].get(), lm))

            def make_lines(**kwargs):
                # for ln in list(line_matrix):
                for key, ln in line_matrix.items():
                    # lm = line_matrix[ln]
                    ln['line'] = self.canvas.create_line(self.get_coords(ln), **kwargs)
                    self.canvas.coords(ln['line'], self.get_coords(ln))
                    match key[0]:
                        case 'h':
                            ln['direction'] = 'y'
                        case 'v':
                            ln['direction'] = 'x'

            make_lines(width=debug_lt, fill='red')

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
            line_set_length = len(line_matrix)

            # global/instance so reusable for <B1-Motion> callback
            self.line_index = 'h0' # req. init value if spinbox used first, fix todo
            self.line_direction = 'x' # str, again req. ^^

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

            return line_matrix

        def init_spinbox(self, ln):
            lm = self.line_matrix[ln]
            
            def try_get(txtvar, func):
                try:
                    txtvar.set(func(txtvar.get(), ln))
                # empty field -> expected floating-point number but got ""
                except TclError: # as e:
                    return # print(e)

            self.pref_pixel_ref = False
            # lm['txtvar/trace'] for removing trace later, unfinished
            if self.pref_pixel_ref:
                inc = 1
                limit = self.line_matrix[ln[0] + '1']['ogpos'] \
                    - self.line_matrix[ln[0] + '1']['conv']
                lm['txtvar'] = txtvar = IntVar(root, lm['pos'].get() - lm['conv'])
                lm['trace'] = txtvar.trace_add("write", lambda *_: try_get(txtvar, move_spinbox_conv))
            else:
                inc = self.img['sample']
                limit = self.line_matrix[ln[0] + '1']['unconv'].get()
                lm['txtvar'] = txtvar = lm['unconv'] # self.unconv(lm)
                lm['trace'] = txtvar.trace_add("write", lambda *_: try_get(txtvar, move_spinbox_unconv))

            return ttk.Spinbox(input_frame, increment=inc, from_=0, to=limit,
                               textvariable=txtvar)
                               # command=lambda: self.move_line_spinbox(lm['pos'].get(), ln))
            
        def move_spinbox_unconv(i, line):
            # used in conv, bring back here for unconv # lm = self.line_matrix[line]
            j = conv(i, line)
            move_spinbox(j, line)
            # i = self.unconv(i, lm)
            # lm['unconv'].set(i)

            # self.unconv(self.line_matrix[line])
            return i
    
        # TODO only update if unconv display preference set, alt function?
        # ToDo convert 'og' to 'scaled' by reverse of scale with that display mode
        def move_spinbox_conv(i, line):
            i += self.line_matrix[line]['conv']
            move_spinbox(i, line)
            return(i - self.line_matrix[line]['conv'])

        def move_spinbox(i, line):
            # print(root.getvar(trace_var)) # scope issues?
            # use *args from callback, first is the PYVAR
            # working equivalent:
            #   ~\AppData\Local\Programs\Python\Python312\Lib\tkinter\__init__.py:2861
            #   return self.tk.getint(self.tk.call(
            self.line_index = line # since move_line used elsewhere, todo make opt?
            #  self.line_matrix[line[0] + '0']['conv']
            self.move_line(i)
            
        def init_spinboxes():
            for ln in list(self.line_matrix):
                self.line_matrix[ln]['spinbox'] = init_spinbox(self, ln)
            for i, ln in enumerate(list(self.line_matrix)):
                self.line_matrix[ln]['spinbox'].grid(row=i)
        
        self.pref_pixel_ref = False
            
        #? self.controlidx = 0
        debugc = 'magenta'
        debugc2 = 'black'
        self.lt = 5 # line thickness
        self.min_gap = 10

        root.title("pdfcrop")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        
        im_frame, im_scrollh, im_scrollv, im_scrollbut, input_frame, crop_btn \
            = init_frames(root)
        self.canvas, self.pdf_item = init_canvas(self.lt)
        canvas_a_size(5)

        self.images = {}

        self.active_img = init_image('t-0.png')
        self.img = self.images[self.active_img]
    
        im_scrollbut['command'] = lambda: self.image_scale(
            root, self.img, 0)

        # lt, line thickness: line coords drawn from center of line width, (0,0) cuts off left edge

        self.line_matrix = init_lines(self.lt)

        init_spinboxes()
        
        # init_menu()
        self.menubar = MenuBar(root)
        
        # root.resizable(FALSE, FALSE)

        # root.attributes('-topmost', 1)
        # print(root.tk.eval('wm stackorder '+str(root)))

        # binds

        im_scrollbut.bind('<Button-2>', lambda e:
                          self.canvas.itemconfigure(self.pdf_item, image=self.img['og']))
        im_scrollbut.bind('<Button-3>', lambda e: canvas_a_size(5))
        self.canvas.bind('<Button-1>', self.get_line)
        self.canvas.bind('<B1-Motion>', self.move_line_mevent)
        # crop_btn.bind('<Button-1>', self.crop_btn_event)

    def unconv(self, i, lm):
        noborder = i - lm['conv'] # subtracts border
        og = noborder * self.img['sample']
        return og

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
        
    def get_line(self, event):
        diffs = {}

        # this method only checks the necessary xy, test perfance diff?
        for line in ['h0', 'h1']:
            liney = abs(event.y - self.line_matrix[line]['pos'].get())
            inity = abs(event.y - self.line_matrix[line]['ogpos'])
            diff = min(liney, inity)
            diffs[line] = diff
        for line in ['v0', 'v1']:
            linex = abs(event.x - self.line_matrix[line]['pos'].get())
            initx = abs(event.x - self.line_matrix[line]['ogpos'])
            diff = min(linex, initx)
            diffs[line] = diff

        # for line in self.line_set:
        #     x = abs(event.x - self.canvas.coords(self.line_set[line]['canv'])[0])
        #     y = abs(event.y - self.canvas.coords(self.line_set[line]['canv'])[1])
        #     diff = min(x, y)
        #     diffs[line] = diff
        # for line in list(self.line_matrix):
        #     x = abs(event.x - self.line_matrix[line][0])
        #     y = abs(event.y - self.line_matrix[line][1])
        #     diff = min(x, y)
        #     diffs[line] = diff

        self.line_index = min(diffs, key=diffs.get) # TODO type hint error
        self.line_direction = self.line_matrix[self.line_index]['direction']

        # if self.line_index >= line_set_length: # >= as 0-indexed
        #     self.line_index -= line_set_length
        self.move_line_mevent(event)

    # return same coordinates but convert any DoubleVar to its value
    def get_coords(self, ln) -> tuple:
        coords = ln['coords']
        return tuple(x.get() if type(x) is IntVar else x for x in coords)
        # match coords[0]:
        #     case 'h': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
        #     case 'v': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
    
            
    def move_line_mevent(self, event): # mouse event
        i = getattr(event, self.line_direction)
        self.move_line(i) # getattr speed?
        # TODO temporarily remove trace for unnecssary once back-forth
        lm = self.line_matrix[self.line_index]
        trace = lm['trace']
        txtvar = lm['txtvar']
        # print(IntVar(root, sbox.cget('textvariable')).trace_info())
        # root.setvar(sbox.cget("textvariable"), i)
        # print(root.getvar(sbox.cget("textvariable")))
        # print(root.getvar(sbox.cget("textvariable")))
        [((mode,), cbname)] = txtvar.trace_info()
        # print(lm['spinbox'].cget(""))
        # txtvar.trace_remove(mode, cbname)
        if not self.pref_pixel_ref:
            i = self.unconv(i, lm)
        self.line_matrix[self.line_index]['spinbox'].set(i)
        
        # txtvar.trace_add(mode, cbname)
        
    def move_line(self, i):
        # if isinstance(input, Event):
        #     x = event.x
        #     y = event.y
        # else:
        #     x = event[0]
        #     y = event[1]

        line = self.line_index
        lm = self.line_matrix

        # ci = self.canvas.coords(line_set_init[ln])
        # orient = ln % 2 == 0
        # if orient and y >= ci[1]:
        #     self.canvas.coords(line, c[0], y, c[2], y)
        # elif not orient and x >= ci[0]:
        #     self.canvas.coords(line, x, c[1], x, c[3])
        # print(x, self.canvas.coords(line_set[3])[0])

        # print(y, self.canvas.coords(self.line_set[ln]['canv']))

        def update(ln, i):
            ln['pos'].set(i)
            coords = self.get_coords(ln)
            self.canvas.coords(ln['line'], coords)
            # ln['spinbox'].set(conv(i, ln))

        # inequality differs between 1/2
        # coordinate (matrix, parallel & self) differs between hor/vert
        # parallel id differs, but naturally paired between h or v
        ln = lm[line]
        match line:
            case 'h0' if (i >= ln['ogpos'] and
                          i < lm['h1']['pos'].get() - self.min_gap):
                update(ln, i)
            case 'h1' if (i <= ln['ogpos'] and
                          i > lm['h0']['pos'].get() + self.min_gap):
                update(ln, i)
            case 'v0' if (i >= ln['ogpos'] and
                          i < lm['v1']['pos'].get() - self.min_gap):
                update(ln, i)
            case 'v1' if (i <= ln['ogpos'] and
                          i > lm['v0']['pos'].get() + self.min_gap):
                update(ln, i)

    # scroll guillotine with bar
    def image_scale(self, root, image, factor):
        img = image['og']
        sample = image['sample']
        if factor == 0:
            # no pre-subsample filtering / downscale => aliasing
            scaled = img.subsample(sample)
        else:
            scaled = img.zoom(factor)
        root.image = scaled # maintain reference w/o PIL
        self.canvas.itemconfigure(self.pdf_item, image=scaled)
        image['scaled'] = scaled
        canvas_o = self.lt * 2
        self.canvas['scrollregion']=(0, 0, scaled.width() + canvas_o,
                                     scaled.height() + canvas_o)

    def canvas_fit(self, img):
        self.canvas['width']  = img.width() + self.lt*2  # + (self.lt - self.bd) * 2
        self.canvas['height'] = img.height() + self.lt*2 # + (self.lt - self.bd) * 2

    # def addLabel(self, txt):
    #     ttk.Label(mainframe, text=txt, background="red"
    #               ).grid(column=0, row=self.controlidx)
    #     self.controlidx += 1

if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(2)
    root = Tk()
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
