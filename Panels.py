import tkinter as tk
from tkinter import ttk
from _tkinter import TclError

from tkinter import filedialog as fd

from math import ceil
from formula import a_sizer
from pathlib import Path
from ctypes import windll

from tkinter.constants import DISABLED, NSEW

class MenuBar:
    # self not necessary?
    def __init__(self, root):
        root.option_add('*tearOff', False)
        menubar = tk.Menu(root)
        root['menu'] = menubar
        menu_file = tk.Menu(root)
        menubar.add_cascade(label='File', menu=menu_file)
        menu_file.add_command(label='Open...', command = fd.askopenfilename)
        menu_file.add_command(label='Save', command = lambda: print('save PLACEHOLDER'))
        menu_file.add_command(label='Save As...', command = fd.asksaveasfilename)
        menu_edit = tk.Menu(root)
        menubar.add_cascade(label='Edit', menu=menu_edit)
        menu_edit.add_command(label='Preset 1')
        menu_edit.add_command(label='A5')
        menu_view = tk.Menu(root)
        menubar.add_cascade(label='View', menu=menu_view)
        menu_view.add_command(label='Portrait/Landscape')
        menu_help = tk.Menu(root)
        menubar.add_cascade(label='Help', menu=menu_help)
        menu_help.add_command(label='Github')
        menu_help.add_command(label='email@test')
        menu_help.entryconfigure('email@test', state=DISABLED) # copy symbol

class PdfCanvas:
    """Widget collection for PDF display and guideline interaction."""
    
    bd = 10
    """Image subframe border between canvas and scrollbars."""
    lt = 5
    """Line thickness also decides internal canvas padding."""
    # lt, line thickness: line coords drawn from center of line width, (0,0) cuts off left edge

    def __init__(self, root, master):
        self.root = root
        self.master = master
        subframe_scrollbut=ttk.Frame(master)#tk., bd=1, bg=debugc)
        subframe_scrollbut.grid_propagate(False)
        subframe_scrollbut.grid(column=1, row=0, sticky=NSEW)
        subframe_scrollbut.columnconfigure(0, weight=1)
        subframe_scrollbut.rowconfigure(0, weight=1)

        subframe_image=tk.Frame(master, relief='sunken', bd=self.bd)
        subframe_image.grid(column=0, row=1)
        subframe_image.columnconfigure(0, weight=1)
        subframe_image.rowconfigure(0, weight=1)

        im_scrollh=ttk.Scrollbar(master, orient='horizontal')
        im_scrollh.grid(column=0, row=0, sticky='we')

        im_scrollv=ttk.Scrollbar(master, orient='vertical')
        im_scrollv.grid(column=1, row=1, sticky='ns')

        self.im_scrollbut=ttk.Button(subframe_scrollbut)
        self.im_scrollbut.grid()

        # def init_canvas(lt):            
        self.canvas=tk.Canvas(subframe_image, bg='grey',
            highlightthickness = 0, highlightcolor = 'white', # todo I think was just for testing
            xscrollcommand=im_scrollh.set, yscrollcommand=im_scrollv.set)
               # scrollregion=(0,0,width,height))
        # im_scrollh['command']=canvas.xview
        # im_scrollv['command']=canvas.yview
        # print(self.im_canvas['highlightthickness'])
        self.canvas.grid(sticky=NSEW)

        # anchor nw for guillotine metaphor (todo opt)
        self.raster = self.canvas.create_image(self.lt, self.lt, anchor='nw')

        # return canvas, pdf_item

        self.images = {}

    def size(self, width, height):
        self.canvas['width']=str(width + self.lt)+'m'
        self.canvas['height']=str(height + self.lt)+'m'

    def a_size(self, a_size):
        """A-series paper size eg. A4
        # TODO other standard print sizes eg. US
        # not used once imaged resized
        """
        width, height = a_sizer(a_size)
        self.size(width, height)

    # scroll guillotine with bar
    def canvas_fit(self, img):
        self.canvas['width']  = img.width() + self.lt*2  # + (self.lt - self.bd) * 2
        self.canvas['height'] = img.height() + self.lt*2 # + (self.lt - self.bd) * 2

    def image_scale(self, root, image, factor):
        img = image['og']
        sample = image['sample']
        if factor == 0:
            # no pre-subsample filtering / downscale => aliasing
            scaled = img.subsample(sample)
        else:
            scaled = img.zoom(factor)
        root.image = scaled # maintain reference w/o PIL
        self.canvas.itemconfigure(self.raster, image=scaled)
        image['scaled'] = scaled
        canvas_o = self.lt * 2
        self.canvas['scrollregion']=(0, 0, scaled.width() + canvas_o,
                                     scaled.height() + canvas_o)

    def set_image(self, filename):
        i_file = Path(filename)
        name = i_file.stem # todo ^ combine
        # todo hc mode opt to use bitmap (like pdf.js)
        og = tk.PhotoImage(master=self.root, file=filename) # master=self.im_canvas

        # calc nearest integer scaling to fit canvas
        subx = (float(self.canvas['width'])  + self.lt) / og.width()
        suby = (float(self.canvas['height']) + self.lt) / og.height()
        sample = ceil(1/min(subx, suby))

        self.pdf = {'og': og, 'path': filename, 'sample': sample}
        self.images[name] = self.pdf
        self.image_scale(self.root, self.pdf, 0)

        self.canvas_fit(self.pdf['scaled'])

        return name

class CanvasLines:
    line_matrix = {} # : dict
    pref_pixel_ref = False
    min_gap = 10
    
    def __init__(self, root, canvas, pdf):
        lt = 5 # line thickness !!!!! dupe, inherit from PdfCanvas
        self.sample = pdf['sample']
        """unconv, move_line_mevent"""
        self.canvas = canvas
        """init, move_line.update"""
        
        debug_lt = lt
        lineo = lt//2 #-(lt%2)
        pdf = pdf['scaled']
        """init"""
        xe = pdf.width()  + lt * 2
        ye = pdf.height() + lt * 2

        # NSEW unsorted list() order matters for self.move_line
        # self.line_matrix = {}
        for ln in ['h0', 'h1', 'v0', 'v1']:
            lm = self.line_matrix[ln] = {}
            p = tk.IntVar(root) # type check in get_coords
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
            lm['unconv'] = tk.IntVar(root, self.unconv(lm['pos'].get(), lm['conv'], self.sample))

        WIDTH = debug_lt
        FILL = 'red'
        # for ln in list(line_matrix):
        for key, ln in self.line_matrix.items():
            # lm = line_matrix[ln]
            ln['line'] = self.canvas.create_line(self.get_coords(ln), width=WIDTH, fill=FILL)
            self.canvas.coords(ln['line'], self.get_coords(ln))
            match key[0]:
                case 'h':
                    ln['direction'] = 'y'
                case 'v':
                    ln['direction'] = 'x'

    def get_coords(self, ln) -> tuple:
        """Return coordinate values unaltered, retrieving actual value
        of any Int/DoubleVar, other coordinate values are constant.
        """
        coords = ln['coords']
        return tuple(x.get() if type(x) is tk.IntVar else x for x in coords)
        # match coords[0]:
        #     case 'h': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
        #     case 'v': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)

    def unconv(self, i, conv, sample):
        noborder = i - conv # subtracts border
        og = noborder * sample
        return og

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
            
    def move_line_mevent(self, event): # mouse event
        i = getattr(event, self.line_direction)
        self.move_line(i) # getattr speed?
        # TODO temporarily remove trace for unnecssary once back-forth
        conv = self.line_matrix[self.line_index]['conv']
        # trace = lm['trace']
        # txtvar = lm['txtvar']
        # # print(IntVar(root, sbox.cget('textvariable')).trace_info())
        # # root.setvar(sbox.cget("textvariable"), i)
        # # print(root.getvar(sbox.cget("textvariable")))
        # # print(root.getvar(sbox.cget("textvariable")))
        # [((mode,), cbname)] = txtvar.trace_info()
        # # print(lm['spinbox'].cget(""))
        # # txtvar.trace_remove(mode, cbname)
        if not self.pref_pixel_ref:
            i = self.unconv(i, conv, self.sample)
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

class LineSpinBox:
    def __init__(self, line_matrix, master, sample, pref_pixel_ref, canvas_lines):
        self.canvas_lines = canvas_lines
        self.line_matrix = line_matrix # ! for conv
        self.sample = sample # self.img['sample']
        """init just sample, for conv otherwise nest lambda as func in try_get?"""

        def init_spinbox(ln):
            # def init_spinbox(self, ln):
            lm = line_matrix[ln]


            def try_get(txtvar, func):
                try:
                    txtvar.set(func(txtvar.get(), ln))
                # empty field -> expected floating-point number but got ""
                except TclError: # as e:
                    return # print(e)

            # lm['txtvar/trace'] for removing trace later, unfinished
            if pref_pixel_ref:
                inc = 1
                limit = line_matrix[ln[0] + '1']['ogpos'] \
                    - line_matrix[ln[0] + '1']['conv']
                lm['txtvar'] = txtvar = tk.IntVar(root, lm['pos'].get() - lm['conv'])
                lm['trace'] = txtvar.trace_add("write", lambda *_: try_get(txtvar, self.move_spinbox_conv))
            else:
                inc = sample # self.img['sample']
                limit = line_matrix[ln[0] + '1']['unconv'].get()
                lm['txtvar'] = txtvar = lm['unconv'] # self.unconv(lm)
                lm['trace'] = txtvar.trace_add("write", lambda *_: try_get(txtvar, self.move_spinbox_unconv))

            return ttk.Spinbox(master, increment=inc, from_=0, to=limit,
                               textvariable=txtvar)
                               # command=lambda: self.move_line_spinbox(lm['pos'].get(), ln))

        for ln in list(line_matrix):
            line_matrix[ln]['spinbox'] = init_spinbox(ln)
        for i, ln in enumerate(list(line_matrix)):
            line_matrix[ln]['spinbox'].grid(row=i)

    def conv(self, i, line):
        """Converts from unscaled value to scaled (I think)"""
        i = (i / self.sample
             + self.line_matrix[line]['conv'])
        return i

    # todo make these @classmethod?
    def move_spinbox_unconv(self, i, line):
        # used in conv, bring back here for unconv # lm = self.line_matrix[line]
        j = self.conv(i, line)
        self.move_spinbox(j, line)
        # i = self.unconv(i, lm)
        # lm['unconv'].set(i)

        # self.unconv(self.line_matrix[line])
        return i

    # TODO only update if unconv display preference set, alt function?
    # ToDo convert 'og' to 'scaled' by reverse of scale with that display mode
    def move_spinbox_conv(self, i, line, line_matrix):
        i += line_matrix[line]['conv']
        self.move_spinbox(i, line)
        return(i - line_matrix[line]['conv'])

    def move_spinbox(self, i, line):
        # print(root.getvar(trace_var)) # scope issues?
        # use *args from callback, first is the PYVAR
        # working equivalent:
        #   ~\AppData\Local\Programs\Python\Python312\Lib\tkinter\__init__.py:2861
        #   return self.tk.getint(self.tk.call(
        self.line_index = line # since move_line used elsewhere, todo make opt?
        #  self.line_matrix[line[0] + '0']['conv']
        self.canvas_lines.move_line(i)

if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    PdfCanvas(root, root)
    root.mainloop()
