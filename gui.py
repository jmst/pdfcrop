import sys
from ctypes import windll

from tkinter import (Tk, StringVar, DoubleVar, Event,
                     Menu, Canvas, PhotoImage, Frame,
                     NORMAL, DISABLED, TRUE, FALSE)
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.ttk import Button
# existing ttk.Widgets will still work as named ttk., so replace them
# existing tk.Frame options fail # from tkinter.ttk import Frame
from math import sqrt, ceil
# from PIL import Image
from formula import a_sizer

class TkGui:
    
    def __init__(self, root):
        #? self.controlidx = 0
        full = 'NSEW' # sticky
        debugc = 'magenta'
        debugc2 = 'black'

        ttk.Style().configure("debug-bg.TFrame", background=debugc)
        ttk.Style().configure("debug-fg.TFrame", background=debugc2)
        
        root.title("pdfcrop")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        mainframe=ttk.Frame(root)
        mainframe.grid(sticky=full)
        mainframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=0)
        mainframe.rowconfigure(0, weight=0)
        mainframe.rowconfigure(1, weight=1)

        ## north top_frame
        top_frame=ttk.Frame(mainframe, borderwidth=1, style='debug-bg.TFrame')
        top_frame.grid(row=0, sticky="we", columnspan=2)
        top_frame.columnconfigure(0, weight=0)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(1, weight=0)

        fn_label = ttk.Label(top_frame, text="File: ")#, background="red")
        fn_label.grid(column=0, row=0)
        fn_entry = ttk.Entry(top_frame, background="red")
        fn_entry.grid(column=1, row=0, sticky="we")

        ## west ui_frame
        ui_frame=ttk.Frame(mainframe, borderwidth=20, relief="ridge",
                           style="debug-bg.TFrame",
                           width=100, height=100)
        ui_frame.grid(column=0, row=1, ipadx="5", sticky=full)
        ui_frame.columnconfigure(0, weight=1)
        ui_frame.rowconfigure(0, weight=1)
        ui_frame.rowconfigure(1, weight=1)

        ## east im_frame
        #       image canvas + mouse interactive guidelines
        
        # TODO other standard print sizes eg. US
        a_size = 5 # A-series paper size eg. A4
        height=a_sizer(a_size)
        width=height/sqrt(2)

        # im_frame: Image frame
        self.bd = 10 # borderwidth
        # container Frame to have different canvas border colour to background
        # ? redundant by using canvas bg instead?
        # ! no, helps logically organise, less rows and columns with subdivision
        im_frame_container=ttk.Frame(mainframe)#, relief='flat')#, bd=self.bd)
        im_frame=Frame(im_frame_container, relief='sunken', bd=self.bd)
        im_scrollh=ttk.Scrollbar(im_frame_container, orient='horizontal')
        im_scrollv=ttk.Scrollbar(im_frame_container, orient='vertical')
        im_frame_scrollbut=Frame(im_frame_container, bd=1, bg=debugc)
        im_frame_scrollbut.grid_propagate(False)
        im_scrollbut=Button(im_frame_scrollbut)#, style='debug-bg.TFrame') # change style dims
        ## grid
        # grid indexes 'reset' in container
        im_frame_container.grid(column=1, row=1, sticky='n')
        im_frame.grid(column=0, row=1, ipadx=self.bd, ipady=self.bd)
        # im_frame.grid_propagate(False)
        im_scrollh.grid(column=0, row=0, sticky='we')
        im_scrollv.grid(column=1, row=1, sticky='ns')
        im_frame_scrollbut.grid(column=1, row=0, sticky=full)
        im_scrollbut.grid()
        ## grid configure
        im_frame.columnconfigure(0, weight=1)
        im_frame.rowconfigure(0, weight=1)
        im_frame_scrollbut.columnconfigure(0, weight=1)
        im_frame_scrollbut.rowconfigure(0, weight=1)
        ## For finding dims for scrollbut
        # root.update_idletasks()
        # print(im_frame_scrollbut['width'])
        # print(im_frame_container.grid_bbox(1,0))

        # print(im_scrollh['style'])
        # print(im_scrollh.winfo_class())
        self.canvas=Canvas(im_frame,
                           width=str((width-self.bd))+'m',
                           height=str((height-self.bd))+'m',
                           highlightthickness = 0,
                           highlightcolor = 'white',
                           bg='grey',
                           xscrollcommand=im_scrollh.set,
                           yscrollcommand=im_scrollv.set)
                              # scrollregion=(0,0,width,height))
        # im_scrollh['command']=self.canvas.xview
        # im_scrollv['command']=self.canvas.yview
        # print(self.im_canvas['highlightthickness'])
        self.canvas.grid(sticky=full)

        #### functionality
        
        ### image canvas
        # make hc mode opt to use bitmap (like pdf.js)
        ogpdf = PhotoImage(master=root, file='t-0.png') # master=self.im_canvas
        im_scrollbut['command'] = lambda: self.image_scale(root, ogpdf, 0)
        self.lt = 5 # line thickness
        # anchor nw for guillotine metaphor (opt)
        self.pdfview = self.canvas.create_image(self.lt, self.lt, anchor='nw')
        # calc nearest integer scaling to fit canvas
        subx = (float(self.canvas['width'])  + self.lt) / ogpdf.width()
        suby = (float(self.canvas['height']) + self.lt) / ogpdf.height()
        self.sample = ceil(1/min(subx, suby))
        pdf = self.image_scale(root, ogpdf, 0)
        # print(float(self.canvas['height']))
        self.canvas_fit(pdf)
        # print(float(self.canvas['height']))
        # self.image_scale(root, ogpdf, 3)
        # not sure why req. 2 padding, cut off otherwise
        # self.canvas.create_rectangle((2, 2, float(self.canvas['width'])+self.lt,
        #                               float(self.canvas['height'])+self.lt),
        #                              width=self.lt,
        #                              outline='red')
        
        # line coords drawn from center of line width, (0,0) cuts off left edge
        debug_lt = self.lt
        lineo = self.lt//2 #-(self.lt%2)
        lineoffset = self.bd * 2 # self.lt*4 # don't know why lt*4 here
        x0 = lineo
        y0 = lineo
        x1 = int(self.canvas['width']) + lineoffset - lineo - 1 # 1 for 0-index?
        y1 = int(self.canvas['height']) + lineoffset - lineo - 1
        xe = int(self.canvas['width']) + lineoffset
        ye = int(self.canvas['height']) + lineoffset

        # float(self.canvas['height'])+debug_lt*4))

        # line point/position
        self.lp = {'h1': {'coord': y0},
                   'h2': {'coord': y1},
                   'v1': {'coord': x0},
                   'v2': {'coord': x1}}
        
        # NSEW unsorted list() order matters for self.move_line
        self.line_matrix = {}
        for ln in ['h1', 'h2', 'v1', 'v2']:
            lm = self.line_matrix[ln] = {}
            p = DoubleVar(root)
            lm['pos'] = p
            wh = 0
            match ln[0]:
                case 'h':
                    wh = int(self.canvas['height'])
                    lm['coords'] = [0, p, xe, p]
                case 'v':
                    wh = int(self.canvas['width'])
                    lm['coords'] = [p, 0, p, ye]
            match ln[1]:
                case '1':
                    val = lm['conv'] = lineo
                    p.set(val)
                case '2':
                    lm['conv'] = lineoffset - lineo - 1
                    val = wh + lm['conv']
                    p.set(val)
            lm['ogpos'] = p.get()
                
        self.line_matrix_old = {'h1': [0, y0, xe, y0], 
                                'h2': [0, y1, xe, y1], 
                                'v1': [x0, 0, x0, ye], 
                                'v2': [x1, 0, x1, ye]}

        # for ln in self.line_matrix:
        #     coords = self.line_matrix[ln]['coords']
        #     for i, xy in enumerate(coords):
        #         if type(xy) is DoubleVar:
        #             coords[i] = xy.get()
        #     print(self.line_matrix[ln]['coords'], self.line_matrix_old[ln], sep='\n')
            
        # self.line_xy = {}
        # for line in list(self.line_matrix):
        #     self.line_xy[line] = self.line_matrix[line][:2]

        def make_lines(**kwargs):
            for ln in list(self.line_matrix):
                lm = self.line_matrix[ln]

                lm['line'] = self.canvas.create_line(self.get_coords(ln), **kwargs)
                self.canvas.coords(lm['line'], self.get_coords(ln))
                match ln[0]:
                    case 'h':
                        lm['direction'] = 'y'
                    case 'v':
                        lm['direction'] = 'x'

        make_lines(width=debug_lt, fill='red')
        
        # def make_line_set(**kwargs):
        #     set = {}
        #     for ln in list(self.line_matrix):
        #         line = self.canvas.create_line(self.line_matrix[ln]['coords'], **kwargs)
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
        line_set_length = len(self.line_matrix)

        # global/instance so reusable for <B1-Motion> callback
        self.line_index = 'h1' # req. init value if spinbox used first, fix todo
        self.line_direction = 'x' # str, again req. ^^

        self.min_gap = 10

        input_frame=ttk.Frame(ui_frame, width=30, height=10)
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
        #         self.canvas.coords(self.line_matrix[line]['coords'])[xy])

        # for line in list(self.line_set):
        #     hvset(line)

        def make_spinbox(ln):
            lm = self.line_matrix[ln]
            txtvar = lm['pos']
            return ttk.Spinbox(input_frame, increment=1, from_=0, to=100,
                               textvariable=txtvar,
                               command=lambda: self.move_line_spinbox(txtvar.get(), ln))

        for ln in list(self.line_matrix):
            self.line_matrix[ln]['spinbox'] = make_spinbox(ln)

        for i, ln in enumerate(list(self.line_matrix)):
            self.line_matrix[ln]['spinbox'].grid(row=i)
        
        minimap=ttk.Frame(ui_frame, style="debug-fg.TFrame")
        input_frame.grid(column=0, row=0)
        minimap.grid(column=0, row=1, sticky=full)

        # menu
        root.option_add('*tearOff', False)
        e = "test"
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

        # root.resizable(FALSE, FALSE)

        # root.attributes('-topmost', 1)
        # print(root.tk.eval('wm stackorder '+str(root)))

        # binds

        self.canvas.bind('<Button-1>', self.get_line)
        self.canvas.bind('<B1-Motion>', self.move_line_mevent)

    def get_line(self, event):
            diffs = {}

            # this method only checks the necessary xy, test perfance diff?
            for line in ['h1', 'h2']:
                liney = abs(event.y - self.line_matrix[line]['pos'].get())
                inity = abs(event.y - self.line_matrix[line]['ogpos'])
                diff = min(liney, inity)
                diffs[line] = diff
            for line in ['v1', 'v2']:
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

    def get_coords(self, ln):
        lm = self.line_matrix[ln]['coords']
        match ln[0]:
            case 'h': return tuple(x.get() if type(x) is DoubleVar else x for x in lm)
            case 'v': return tuple(x.get() if type(x) is DoubleVar else x for x in lm)
        
            
    def move_line_mevent(self, event): # mouse event
        self.move_line(getattr(event, self.line_direction)) # getattr speed?
        
    def move_line_spinbox(self, i, line):
        self.line_index = line
        self.move_line(i)
        
    def move_line(self, i):
        # if isinstance(input, Event):
        #     x = event.x
        #     y = event.y
        # else:
        #     x = event[0]
        #     y = event[1]

        ln = self.line_index
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
            lm[ln]['pos'].set(i)
            coords = self.get_coords(ln)
            self.canvas.coords(lm[ln]['line'], coords)

        # inequality differs between 1/2
        # coordinate (matrix, parallel & self) differs between hor/vert
        # parallel id differs, but naturally paired between h or v
        match ln:
            case 'h1' if (i >= lm[ln]['ogpos'] and
                          i < lm['h2']['pos'].get() - self.min_gap):
                update(ln, i)
            case 'h2' if (i <= lm[ln]['ogpos'] and
                          i > lm['h1']['pos'].get() + self.min_gap):
                update(ln, i)
            case 'v1' if (i >= lm[ln]['ogpos'] and
                          i < lm['v2']['pos'].get() - self.min_gap):
                update(ln, i)
            case 'v2' if (i <= lm[ln]['ogpos'] and
                          i > lm['v1']['pos'].get() + self.min_gap):
                update(ln, i)

    # scroll guillotine with bar
    def image_scale(self, root, img, factor):
        if factor == 0:
            # no pre-subsample filtering / downscale => aliasing
            scaled = img.subsample(self.sample)
        else:
            scaled = img.zoom(factor)
        self.canvas.itemconfigure(self.pdfview, image=scaled)
        self.canvas['scrollregion']=(0, 0, scaled.width(), scaled.height())
        root.image = scaled # maintain reference w/o PIL
        return scaled

    def canvas_fit(self, img):
        self.canvas['width']  = img.width()  + (self.lt - self.bd) * 2
        self.canvas['height'] = img.height() + (self.lt - self.bd) * 2

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
