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
from math import ceil
# from PIL import Image
from formula import a_sizer

from pathlib import Path

class TkGui:
    
    def __init__(self, root):

        def init_frames():
 
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
            top_frame=ttk.Frame(mainframe, borderwidth=1) #, style='debug-bg.TFrame')
            top_frame.grid(row=0, sticky="we", columnspan=2)
            top_frame.columnconfigure(0, weight=0)
            top_frame.columnconfigure(1, weight=1)
            top_frame.rowconfigure(1, weight=0)

            fn_label = ttk.Label(top_frame, text="File: ")#, background="red")
            fn_label.grid(column=0, row=0)
            fn_entry = ttk.Entry(top_frame, background="red")
            fn_entry.grid(column=1, row=0, sticky="we")

            ## west ui_frame
            ui_frame=ttk.Frame(mainframe, borderwidth=20, relief="ridge")
                               # style="debug-bg.TFrame",
                               # width=100, height=100)
            ui_frame.grid(column=0, row=1, ipadx="5", sticky=full)
            ui_frame.columnconfigure(0, weight=1)
            ui_frame.rowconfigure(0, weight=1)
            ui_frame.rowconfigure(1, weight=1)

            ## east im_frame
            #       image canvas + mouse interactive guidelines

            # im_frame: Image frame
            # self.bd tries to assign to TkGui, reserved?
            # no, can't assign to self from within sub-function, unless passed
            bd = 10 # borderwidth
            # container Frame to have different canvas border colour to background
            # ? redundant by using canvas bg instead?
            # ! no, helps logically organise, less rows and columns with subdivision
            im_frame_container=ttk.Frame(mainframe)#, relief='flat')#, bd=self.bd)
            # non-ttk Frame for specific border, todo theme instead
            im_frame=Frame(im_frame_container, relief='sunken', bd=bd)
            im_scrollh=ttk.Scrollbar(im_frame_container, orient='horizontal')
            im_scrollv=ttk.Scrollbar(im_frame_container, orient='vertical')
            im_frame_scrollbut=ttk.Frame(im_frame_container)#tk., bd=1, bg=debugc)
            im_frame_scrollbut.grid_propagate(False)
            im_scrollbut=Button(im_frame_scrollbut)#, style='debug-bg.TFrame') # change style dims
            ## grid
            # grid indexes 'reset' in container
            im_frame_container.grid(column=1, row=1, sticky='n')
            # ipadding messes with child canvas dimensions
            im_frame.grid(column=0, row=1) #ipadx=self.bd, ipady=self.bd)
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

            input_frame=ttk.Frame(ui_frame, width=30, height=10)

            input_frame.grid(row=0, sticky='s')

            crop = ttk.Button(ui_frame, text='Crop')
            crop.grid(row=1, sticky='n')

            minimap=ttk.Frame(ui_frame, height=100, style="debug-fg.TFrame")

            minimap.grid(column=0, row=2, sticky=full)

            return im_frame, im_scrollh, im_scrollv, im_scrollbut, input_frame

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
            canvas.grid(sticky=full)

            def canvas_a_size(a_size): # A-series paper size eg. A4
                # TODO other standard print sizes eg. US
                # not used once imaged resized
                width, height = a_sizer(a_size)
                canvas['width']=str(width + lt)+'m'
                canvas['height']=str(height + lt)+'m'
            canvas_a_size(5)

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
            lineoffset = lt * 4 # lt*4 # don't know why lt*4 here
            x0 = lineo
            y0 = lineo
            pdf = self.images[self.active_img]['scaled']
            x1 = pdf.width() + lineoffset - lineo - 1 # 1 for 0-index?
            y1 = pdf.height() + lineoffset - lineo - 1
            xe = pdf.width() + lt * 2
            ye = pdf.height() + lt * 2

            # float(self.canvas['height'])+debug_lt*4))

            # line point/position
            lp = {'h1': {'coord': y0},
                  'h2': {'coord': y1},
                  'v1': {'coord': x0},
                  'v2': {'coord': x1}}

            # NSEW unsorted list() order matters for self.move_line
            line_matrix = {}
            for ln in ['h1', 'h2', 'v1', 'v2']:
                lm = line_matrix[ln] = {}
                p = DoubleVar(root)
                lm['pos'] = p
                dim = 0
                match ln[0]:
                    case 'h':
                        dim = pdf.height()
                        lm['coords'] = [0, p, xe, p]
                    case 'v':
                        dim = pdf.width()
                        lm['coords'] = [p, 0, p, ye]
                match ln[1]:
                    case '1':
                        val = lm['conv'] = lineo
                        p.set(val)
                    case '2':
                        lm['conv'] = lt + lineo # left border + line width pad
                        val = dim + lm['conv']
                        p.set(val)
                lm['ogpos'] = p.get()

            line_matrix_old = {'h1': [0, y0, xe, y0], 
                                    'h2': [0, y1, xe, y1], 
                                    'v1': [x0, 0, x0, ye], 
                                    'v2': [x1, 0, x1, ye]}

            # for ln in line_matrix:
            #     coords = line_matrix[ln]['coords']
            #     for i, xy in enumerate(coords):
            #         if type(xy) is DoubleVar:
            #             coords[i] = xy.get()
            #     print(line_matrix[ln]['coords'], line_matrix_old[ln], sep='\n')

            # self.line_xy = {}
            # for line in list(line_matrix):
            #     self.line_xy[line] = line_matrix[line][:2]

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
            self.line_index = 'h1' # req. init value if spinbox used first, fix todo
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

        def init_spinboxes():
        
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

        def init_menu():
        
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
        
        #? self.controlidx = 0
        full = 'NSEW' # sticky
        debugc = 'magenta'
        debugc2 = 'black'
        self.lt = 5 # line thickness
        self.min_gap = 10
        
        im_frame, im_scrollh, im_scrollv, im_scrollbut, input_frame \
            = init_frames()
        self.canvas, self.pdf_item = init_canvas(self.lt)

        self.images = {}

        self.active_img = init_image('t-0.png')
    
        im_scrollbut['command'] = lambda: self.image_scale(root, self.images[self.active_img], 0)

        # lt, line thickness: line coords drawn from center of line width, (0,0) cuts off left edge

        self.line_matrix = init_lines(self.lt)

        init_spinboxes()

        init_menu()
        
        # root.resizable(FALSE, FALSE)

        # root.attributes('-topmost', 1)
        # print(root.tk.eval('wm stackorder '+str(root)))

        # binds

        im_scrollbut.bind('<Button-2>', lambda e: self.canvas.itemconfigure(
            self.pdf_item, image=self.images[self.active_img]['og']))
        im_scrollbut.bind('<Button-3>', lambda e: canvas_a_size(5))
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

    # return same coordinates but convert any DoubleVar to its value
    def get_coords(self, ln):
        coords = ln['coords']
        return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
        # match coords[0]:
        #     case 'h': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
        #     case 'v': return tuple(x.get() if type(x) is DoubleVar else x for x in coords)
    
            
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
            ln['pos'].set(i)
            coords = self.get_coords(ln)
            self.canvas.coords(ln['line'], coords)

        # inequality differs between 1/2
        # coordinate (matrix, parallel & self) differs between hor/vert
        # parallel id differs, but naturally paired between h or v
        line = lm[ln]
        match ln:
            case 'h1' if (i >= lm[ln]['ogpos'] and
                          i < lm['h2']['pos'].get() - self.min_gap):
                update(line, i)
            case 'h2' if (i <= line['ogpos'] and
                          i > lm['h1']['pos'].get() + self.min_gap):
                update(line, i)
            case 'v1' if (i >= line['ogpos'] and
                          i < lm['v2']['pos'].get() - self.min_gap):
                update(line, i)
            case 'v2' if (i <= line['ogpos'] and
                          i > lm['v1']['pos'].get() + self.min_gap):
                update(line, i)

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
        self.canvas['scrollregion']=(0, 0, scaled.width() + self.lt * 2, scaled.height() + self.lt * 2)

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
