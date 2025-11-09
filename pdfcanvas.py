import tkinter as tk
import tkinter.ttk as ttk

from math import ceil
from formula import a_sizer
from pathlib import Path

import pymupdf

import start

# TODO
# scale crop line with zoom
# opt border around canvas edge


class CanvasLines:
    pref_pixel_ref = False
    flipbit = {'0': '1', '1': '0'}
    
    def __init__(self, root, canvas, pdf = None):
        # intvar # type check in get_coords
        self.line_matrix = {key: {'pos': tk.IntVar(root), 'direction': None}
                            for key in ['h0', 'h1', 'v0', 'v1']}
        if pdf: #!? redundant, always use canvas after scale
            self.sample = pdf['sample']
            pdf = pdf['scaled']
            width, height = pdf.width(), pdf.height()
        else:
            width = int(canvas['width'])
            height = int(canvas['height'])
            self.sample = 1
        
        self.lt = 5 # line thickness !!!!! dupe, inherit from PdfCanvas
        self.min_gap = self.lt
        self.lineo = self.lt//2 #-(lt%2) # +1 canvas 0-indexed

        """unconv, move_line_mevent"""
        self.canvas = canvas
        """init, move_line.update"""
        
        debug_lt = self.lt
        
        # NSEW unsorted list() order matters for self.move_line
        # self.line_matrix = {}

        self.set_lines(width, height)

        WIDTH = debug_lt
        FILL = 'red'
        
        # for ln in list(line_matrix):
        for key, ln in self.line_matrix.items():
            # lm = line_matrix[ln]
            ln['line'] = self.canvas.create_line(self.get_coords(ln),
                                                 width=WIDTH,
                                                 fill=FILL)
            self.canvas.coords(ln['line'], self.get_coords(ln))
            match key[0]:
                case 'h':
                    ln['direction'] = 'y'
                case 'v':
                    ln['direction'] = 'x'

    def set_lines(self, width, height):
        """ ogpos and its pair bound upper & lower, including after convert
            instead of: lm['limit'] = [xy]e - self.lineo - 1
        """
        def init_pos(dim):
            match ln[1]:
                case '0':
                    val = lm['conv'] = self.lineo
                case '1':
                    # line width pad + entire left border (line thickness)
                    # simpler as 3x self.lineo + 1 (line centre)?
                    lm['conv'] = self.lineo + self.lt
                    print(dim)
                    val = dim - self.lineo - self.lt #- (self.lt % 2) # -1 because 0-indexed coords?
                case _: # can things even get this far if line index is wrong?
                    val = -1
            p.set(val)
            lm['ogpos'] = p.get() # can't combine with set?
        
        for ln, lm in self.line_matrix.items(): # ln line lm sub-matrix
            lm = self.line_matrix[ln] 
            p: tk.IntVar = lm['pos']
            
            match ln[0]:
                case 'h':
                    # ? make var for spinbox limit access
                    # ...guessing I meant spinbox sees the dim value instead of
                    #           actual pos so no need to convert, but here?
                    # maybe not seeing as spinbox should interface WITH this
                    init_pos(height)
                    lm['coords'] = [0, p, width, p]
                case 'v':
                    init_pos(width)
                    lm['coords'] = [p, 0, p, height]

            root = self.canvas.winfo_toplevel()
            lm['unconv'] = tk.IntVar(root, self.unconv(lm['pos'].get(),
                                                       lm['conv'],
                                                       self.sample))

    def get_coords(self, ln) -> tuple:
        """Return coordinate values unaltered, retrieving actual value
        of any Int/DoubleVar, other coordinate values are constant.
        """
        coords = ln['coords']
        return tuple(x.get() if type(x) is tk.IntVar else x for x in coords)
        # match coords[0]:
        #     case 'h': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
        #     case 'v': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)

    def unconv(self, i: int, conv: int, sample: int):
        """Unconvert by inverse sample and 'conv' border compensation."""
        # TODO make new line_matrix class the owner of this function
        noborder = i - conv # subtracts border
        og = noborder * sample
        return og

    # bind - initial mouse1 down
    
    def get_line(self, event):
        (x, y) = (event.x, event.y)
        diffs = {}
        # this method only checks the necessary xy, test perfance diff?
        for line in ['h0', 'h1']:
            liney = abs(y - self.line_matrix[line]['pos'].get())
            inity = abs(y - self.line_matrix[line]['ogpos'])
            diff = min(liney, inity)
            diffs[line] = diff
        for line in ['v0', 'v1']:
            linex = abs(x - self.line_matrix[line]['pos'].get())
            initx = abs(x - self.line_matrix[line]['ogpos'])
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

        self.line_id = min(diffs, key=diffs.get) # TODO type hint error
        self.line_direction = self.line_matrix[self.line_id]['direction']

        def get_pair(line):
            return self.line_matrix[line[0] + self.flipbit[line[1]]]
        def pair_lim(id):
            """Negative gap for southwest lines ie. index 1"""
            gap = -self.min_gap if id[1] == '0' else self.min_gap
            lim = get_pair(self.line_id)['pos'].get() + gap
            print(gap, lim)
            return lim
        self.lim = pair_lim(self.line_id)

        # if self.line_index >= line_set_length: # >= as 0-indexed
        #     self.line_index -= line_set_length
        self.move_line_mevent(event)    

    # bind - initial mouse1 down and movement while down
    def move_line_mevent(self, event): # mouse event
        # if isinstance(input, Event):
        #     x = event.x
        #     y = event.y
        # else:
        #     x = event[0]
        #     y = event[1]
        i = getattr(event, self.line_direction)
        line = self.line_id
        lm = self.line_matrix
        ln = lm[line]
        ogpos = ln['ogpos']

        # ci = self.canvas.coords(line_set_init[ln])
        # orient = ln % 2 == 0
        # if orient and y >= ci[1]:
        #     self.canvas.coords(line, c[0], y, c[2], y)
        # elif not orient and x >= ci[0]:
        #     self.canvas.coords(line, x, c[1], x, c[3])
        # print(x, self.canvas.coords(line_set[3])[0])

        # print(y, self.canvas.coords(self.line_set[ln]['canv']))

        # inequality differs between 1/2
        # coordinate (matrix, parallel & self) differs between hor/vert
        # parallel id differs, but naturally paired between h or v

        # match line:
        #     case 'h0' if (i >= ln['ogpos'] and
        #                   i < lm['h1']['pos'].get() - self.min_gap):
        #         update(ln, i)
        #     case 'h1' if (i <= ln['ogpos'] and
        #                   i > lm['h0']['pos'].get() + self.min_gap):
        #         update(ln, i)
        #     case 'v0' if (i >= ln['ogpos'] and
        #                   i < lm['v1']['pos'].get() - self.min_gap):
        #         update(ln, i)
        #     case 'v1' if (i <= ln['ogpos'] and
        #                   i > lm['v0']['pos'].get() + self.min_gap):
        #         update(ln, i)

        match line[1]:
            case '0':
                if  (i <= ogpos):
                     i  = ogpos
                elif i >= (pair := self.lim):
                     i  = pair
            case '1':
                if  (i >= ogpos):
                     i  = ogpos
                elif i <= (pair := self.lim):
                     i  = pair
        if ln['pos'].get() != i:
            self.move_line(i, ln) # getattr speed?
        # TODO temporarily remove trace for unnecssary once back-forth
        conv = self.line_matrix[self.line_id]['conv']
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
        # self.line_matrix[self.line_index]['spinbox'].set(i)
        #       replace with trace mechanism
        
        # txtvar.trace_add(mode, cbname)

    # move_line_mevent, move_spinbox
    def move_line(self, i, ln):
        """line: self.line_index fixed at start of mouse drag event.
                Spinbox passes its line value directly on each event."""
        ln['pos'].set(i)
        coords = self.get_coords(ln)
        self.canvas.coords(ln['line'], coords)
        # ln['spinbox'].set(conv(i, ln))

class PdfCanvas:
    """Widget collection for PDF display and guideline interaction."""
    
    bd = 17 # aligns with scrollbox bar+buttons, hc borders also align
    """Image subframe border between canvas and scrollbars."""
    lt = 5 # TODO odd+cursor at center, prefer in/out? prefer edge cursor mode
    """Line thickness also decides internal canvas padding."""
    # lt, line thickness: line coords drawn from center of line width,
    # (0,0) cuts off left edge
    A_SIZE_DEF = 6

    bnd_mouse_dbg = '<Key-space>'

    internal_width, internal_height = None, None

    def __init__(self, root: tk.Tk, master: ttk.Frame):
        self.root = root # todo swap out root references for master if possible
        self.master = master

        """grid"""
        
        self.master.grid(sticky=tk.NSEW)#==.pack(fill=tk.BOTH, expand=True)#==

        self.master.columnconfigure(0, weight=1) # scroll+canvas
        self.master.columnconfigure(1, weight=0) # scroll
        self.master.rowconfigure(0, weight=0) # scroll
        self.master.rowconfigure(1, weight=1) # canvas

        """scrollbars"""

        im_scrollh=ttk.Scrollbar(self.master, orient=tk.HORIZONTAL)

        subframe_scrollbut=ttk.Frame(self.master) # TODO dark border, may be button
        subframe_scrollbut.grid_propagate(False)
        subframe_scrollbut.columnconfigure(0, weight=1)
        subframe_scrollbut.rowconfigure(0, weight=1)
        self.im_scrollbut=ttk.Button(subframe_scrollbut)#, state=tk.DISABLED)

        im_scrollv=ttk.Scrollbar(self.master, orient=tk.VERTICAL)

        """image"""
        
        # different border to background require subframe
        subframe_image=tk.Frame(self.master, relief=tk.SUNKEN, bd=self.bd)#, bg='red')
        subframe_image.columnconfigure(0, weight=1)
        subframe_image.rowconfigure(0, weight=1)

        # def init_canvas(lt):            
        self.canvas=tk.Canvas(subframe_image, bg='grey',
            highlightthickness = 0, highlightcolor = 'white', # todo I think was just for testing
            xscrollcommand=im_scrollh.set, yscrollcommand=im_scrollv.set)
               # scrollregion=(0,0,width,height))
        im_scrollh['command']=self.canvas.xview
        im_scrollv['command']=self.canvas.yview
        # print(self.im_canvas['highlightthickness'])
        
        # anchor nw for guillotine metaphor (todo opt)
        self.raster = self.canvas.create_image(self.lt, self.lt, anchor='nw')

        # return canvas, pdf_item

        self.images = {}

        # TODO make opt - both a_size and its role as upper bound

        self.canvaslines = CanvasLines(self.root, self.canvas)
        # must initialise canvaslines before
        self.a_size() #5 # empty size + acts as upper bound to image scale
        self.scale(root, None, 1)

        """grid"""
        
        im_scrollh.grid(column=0, row=0, sticky=tk.EW)
        subframe_scrollbut.grid(column=1, row=0, sticky=tk.NSEW) # else hidden
        self.im_scrollbut.grid()        
        
        subframe_image.grid(column=0, row=1, sticky=tk.NSEW)
        self.canvas.grid(sticky=tk.NW) # NSEW

        im_scrollv.grid(column=1, row=1, sticky=tk.NS)


        # ttk.Frame(master).grid(row=2)

        """binds"""
        
        self.img = None
        # No image, no scale to reset
        def e_reset_scale(*_): self.scale(root, self.img, 0)
        # def e_reset_image(_): self.canvas.itemconfig(self.raster, image=self.img['og'])
        self.im_scrollbut['command'] = lambda: self.scale(root, self.img, 2)
        self.im_scrollbut.bind('<Button-3>', lambda _: self.scale(root, self.img, -2))
        self.im_scrollbut.bind('<Button-2>', e_reset_scale) # e_reset_image
        # self.im_scrollbut.bind('<Button-2>', lambda _: self.a_size())
        self.canvas.bind('<Button-1>',  self.canvaslines.get_line)
        self.canvas.bind('<B1-Motion>', self.canvaslines.move_line_mevent)
        # self.canvas.bind('<B1-ButtonRelease>', lambda _: self.root.geometry(""))
        # self.canvas.master.bind('<Configure>', lambda _: self.fit_to_frame())
        self.canvas.master.bind('<Double-Button-1>', self.fit_to_frame)

        # for widget in (self.canvas.bind(seq, func) for seq, func in
        #   ('Button-3', lambda _: self.scale(root, self.img, -1))):
        #     print(widget)

        # x = ((self.canvas, ((lambda _: self.scale(root, self.img, -1), 'Button-3')
        #                 (self.canvaslines.get_line, 'Button-1'))),
        #      (self.im_scrollbut, (("test"))))

        # print(x)

        # gets stuck at seemingly random sizes, regardless of gap, no fucking clue
        def dbg(*_):
            def click(i):
                i, j = ar(i)
                # while i/mn > j/mx: # would always adds 1 once
                #     j += 1
                
                for x, y in (      # clockwise
                        (mn, j),   # h0
                        (w-i, mn), # v1
                        (mn, h-j), # h1
                        (i, mn),   # v0
                ):
                    self.canvas.event_generate("<Button-1>", x=x, y=y)
            self.root.unbind('<Key-space>') # KeyPress-a

            brk = False
            w = float(self.canvas['width'])
            h = float(self.canvas['height'])
            if w < h:
                def ar(i): return i, mx * (i / mn)
            elif w > h:
                def ar(i): return mx * (i / mn), i
            else:
                def ar(i): return i, i
                
            delay = 'idle'
            pause = 200
            gap_bak = self.canvaslines.min_gap
            # todo temp enable crossover for negative values
            gap = self.canvaslines.min_gap = 10 #self.lt//2
            start = 0
            interval = 1

            # clicking beyond gap (+1) breaks it
            mn = min(w, h)/2 #-gap #+ (self.lt // 2) + 1
            mx = max(w, h)/2 #+ (self.lt // 2) + 1
            def dir(i): return i + interval
            def mouser(i):
                nonlocal brk, dir
                if i < mn  and not brk: # int(mn) broke it
                    click(i)
                    i = dir(i)
                    root.after(delay, mouser, i)
                elif i >= mn:
                    brk = True
                    def dir(i): return i - interval
                    i = dir(i)
                    root.after(pause, mouser, i)
                elif i > start and brk:
                    i = dir(i)
                    click(i)
                    root.after(delay, mouser, i)
                else:
                    self.canvaslines.min_gap = gap_bak
                    self.root.bind(self.bnd_mouse_dbg, dbg) # KeyPress-a
            mouser(start)

        # root focused at start so M-SPC opens menu .canvas binds req. focus
        # Key-space intercepts M-SPC
        self.root.bind(self.bnd_mouse_dbg, dbg) # KeyPress-a

    def get_size(self):
        c = self.canvas
        def noborder(x): return int(x) - self.lt
        width, height = map(noborder, (c['width'], c['height']))
        return width, height

    def _set_size(self, w, h):
        c = self.canvas
        c['width'], c['height'] = w, h

    # todo profile this function called exlicitly vs in set_size
    #   runs continuously on resize unlike others in set_size
    def fit_to_frame(self, *_args):
        """Fit canvas to its master frame.
        Only makes sense for empty or free-scaling (non-integer) canvas.
        """
        def dims(frame): return (frame.winfo_width(), frame.winfo_height())
        frame = self.canvas.master
        border = frame['bd'] * 2
        w, h = (x - border for x in dims(frame))
        self._set_size(w, h)
        self.line_scale(w, h)
    
    def set_size(self, width = None, height = None, units = ""):
        if not (width and height):
            self.fit_to_frame()
        else:
            self.internal_width, self.internal_height = width, height
            w, h = (x + self.lt for x in (width, height))
            if units:
                self._set_size(*(str(x) + units for x in (w, h)))
            else:
                self._set_size(width, height)
            self.line_scale(w, h)
        
    def a_size(self, a_size = A_SIZE_DEF):
        """A-series paper size eg. A4
        # TODO other standard print sizes eg. US
        # not used once imaged resized
        """
        width, height = a_sizer(a_size)
        self.set_size(width, height, 'm')

    # scroll guillotine with bar
    def canvas_fit(self, img):
        # + (self.lt - self.bd) * 2
        self.canvas['width']  = img.width() + self.lt*2
        self.canvas['height'] = img.height() + self.lt*2

    def canvas_scale(self, factor):
        """Currently only for/tested int
                Could make negative flip the canvas, or something."""
        width, height = None, None
        if factor == 0:
            # a_size that fits within the window size
            # self.fit_canvas_to_master()
            return
            # no pre-subsample filtering / downscale => aliasing
        elif abs(factor) == 1:
            self.a_size()
        elif factor == -1:
            print("Undefined alternate behaviour to absolute")
        elif -1 < factor < 0:
            print("Negative float invalid.")
        else:
            if factor < -1 and isinstance(factor, int): # 0 < factor < 1
                factor = (1/2)**(abs(factor) - 1) # -2 -> 0.5
            """0<f<1 subsample, >1 zoom"""
            width, height = map(lambda x: x * factor, self.get_size())
            self.set_size(width, height)
        if not (width and height):
            width, height = self.get_size()
        return width, height

    def image_scale(self, root, image, factor):
        # @dispatch method for integer or float?
        img = image['og']
        if factor == 0:
            sample = self.get_sample_to_canvas(img)
            # sample = image['sample']
            scaled = img.subsample(sample)
            # self.fit_to_canvas(image['scaled'])
            # self.fit_canvas_to_master()
        elif factor == 1:
            scaled = img.zoom(1) # def. w/o?
            self.canvaslines.sample = 1
        elif factor < -1:
            self.canvaslines.sample += factor
            factor = abs(self.canvaslines.sample) + 1 # 1 = no zoom, -1 => zoom out once
            scaled = img.zoom(factor)
        elif factor > 1:
            factor += self.canvaslines.sample
            scaled = img.subsample(factor)
            self.canvaslines.sample = factor
            # no pre-subsample filtering / downscale => aliasing
        elif -1 < factor < 0:
            # zoom = abs(factor)
            return # convert -ve float to closest integer zoom factor ie. 0.25 -> 2x zoom out
                        # sqrt until > 1?
        elif 0 < factor < 1:
            # sample = factor
            return # convert +ve float to closest integer subsample
        else:
            scaled = img

        root.image = scaled # maintain reference w/o PIL
        self.canvas.itemconfigure(self.raster, image=scaled)
        image['scaled'] = scaled
        self.canvas_fit(self.pdf['scaled'])

        def pad_dims(pdf):
            canvas_o = self.lt * 2 # ! opt starting offset, would need to + i0, - i1
                # this however is required to set limits properly
            return [dim + canvas_o for dim in [pdf.width(), pdf.height()]]
        (width, height) = pad_dims(scaled)
        
        self.canvas['scrollregion']=(0, 0, width, height)

        return width, height

        # lm = self.canvaslines.line_matrix
        # for ln in lm:
        #     match ln[0]:
        #         case 'h':
        #             lm['line'][2] = scaled.width() + canvas_o
        #         case 'v':
        #             ln['line'][3] = scaled.height() + canvas_o
        # arr = (self.canvas.coords(self.canvaslines.line_matrix['h0']['line']))
        # print(scaled.width)
        # arr[2] = scaled.width() + canvas_o
        # print(arr)
        # print((self.canvas.coords(self.canvaslines.line_matrix['h0']['line']))[2])
        # print(self.canvas.coords(self.canvaslines.line_matrix['h0']['line'], arr))

    def line_scale(self, width, height):
        self.canvaslines.set_lines(width, height)
        for _ln, lm in self.canvaslines.line_matrix.items():
            self.canvaslines.move_line(lm['pos'].get(), lm)
        
    def scale(self, root, image, factor):
        if not image:
            width, height = map(lambda x: x + self.lt,
                                self.canvas_scale(factor))
        else:
            width, height = self.image_scale(root, image, factor)
        self.line_scale(width, height) # hook instead so can just call canvas_scale
        # root.geometry("") # todo only run in manually resized state
                                # that is when that bind disabled

        # calc nearest integer scaling to fit canvas
    # def map_attr(self, obj, *args, prefix = ""):
    #     return (getattr(self.canvas, dim)() for dim in ('winfo_width', 'winfo_height'))
    #         width, height = self.map_attr(self.canvas, 'width', 'height', prefix = 'winfo')
    def get_sample_to_canvas(self, img):
        """Get sample that will scale closest to current canvas size."""
        # (width, height) = (float(self.canvas[x]) + self.lt for x in ('width', 'height'))
        width, height = self.get_size()
        print(self.canvas.winfo_width(), self.canvas.winfo_height())
        print(width, height)
        width, height = (x + self.lt for x in (width, height))
        subx = width / img.width()
        suby = height / img.height()
        sample = ceil(1/min(subx, suby))
        return sample

    def set_image(self, filename):
        i_file = Path(filename)
        name = i_file.stem # todo ^ combine
        # todo hc mode opt to use bitmap (like pdf.js)
        # master=self.im_canvas
        og = tk.PhotoImage(master=self.root, file=filename)

        sample = self.get_sample_to_canvas(og)
        
        self.pdf = {'og': og, 'path': filename, 'sample': sample}
        self.images[name] = self.pdf
        # can't 0 as first initialised within image_scale
        self.pdf['scaled'] = self.pdf['og']
        self.scale(self.root, self.pdf, 0)

        return name

    def open(self, filename):
        pdf = pymupdf.open(filename)
        # self.root.title(Path(filename).name + " - " + self.root.title()) # TODO make root attr
        page_name = "page.png"
        page = pdf[0].get_pixmap().save(page_name)
        
        self.active_img = self.set_image(page_name) # 't-0.png'
        self.img = self.images[self.active_img]
        # self.canvaslines = CanvasLines(self.root, self.canvas, self.img)
        # self.canvas.coords(self.canvaslines.line_matrix['h1']['line'][2])
        
        self.im_scrollbut['state']=tk.NORMAL
        # return self.img

if __name__ == "__main__":
    def main(root: tk.Tk):
        # root.geometry("400x" + str(int(400*(2**0.5))))
        master = ttk.Frame(root)
        PdfCanvas(root, master)#.open("C:/Users/James/Desktop/projects/code/py/pdfcrop/houdini_foundations_19_5_01.pdf")
    start.start(main) # lambda root: PdfCanvas(root, root)
