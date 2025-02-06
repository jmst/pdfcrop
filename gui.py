import sys
from ctypes import windll

from tkinter import (Tk, StringVar,
                     Menu, Canvas, PhotoImage, Frame, Button,
                     NORMAL, DISABLED, TRUE, FALSE)
from tkinter import filedialog as fd
from tkinter import ttk
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

        input_frame=ttk.Frame(ui_frame, width=30, height=10)
        x0 = StringVar(root, '0')
        x0_entry=ttk.Entry(input_frame, textvariable=x0)
        x0_entry.grid(row=0)
        x1 = StringVar(root, '1')
        x1_entry=ttk.Entry(input_frame, textvariable=x1)
        x1_entry.grid(row=1)
        minimap=ttk.Frame(ui_frame, style="debug-fg.TFrame")
        input_frame.grid(column=0, row=0)
        minimap.grid(column=0, row=1, sticky=full)

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
        im_scrollbut=ttk.Button(im_frame_scrollbut)#, style='debug-bg.TFrame') # change style dims
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
        im_scrollbut['command']=lambda: self.image_scale(root, ogpdf, 0)
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
        # print(lineo)
        lineoffset = self.lt*4 # don't know why lt*4 here
        x0 = lineo
        y0 = lineo
        x1 = int(self.canvas['width']) - lineo - 1 + lineoffset # why the -1?
        y1 = int(self.canvas['height']) + self.lt * 3 + lineo
        xe = int(self.canvas['width']) + lineoffset
        ye = int(self.canvas['height']) + lineoffset

        # float(self.canvas['height'])+debug_lt*4))

        h1 = self.canvas.create_line(0, y0, xe, y0)
        h2 = self.canvas.create_line(0, y1, xe, y1)
        v1 = self.canvas.create_line(x0, 0, x0, ye)
        v2 = self.canvas.create_line(x1, 0, x1, ye)
        line_set = [h1, v2, h2, v1] # NESW order matters for move_line
        line_set_length = len(line_set)
        for line in line_set:
            self.canvas.itemconfigure(line, width=debug_lt, fill='red')

        # to check if closest to og pos ie. canvas edge
        # TODO make this optional; og pos != canvas edge circumstance?
        line_set_init = []
        for line in line_set:
            line_set_init.append(self.canvas.create_line(
                self.canvas.coords(line), state='hidden'))

        # global/instance so reusable for <B1-Motion> callback
        self.line_index = 0

        def get_line(event):
            diffs = []
            for line in line_set + line_set_init:
                cd = self.canvas.coords(line)
                x = abs(event.x - cd[0])
                y = abs(event.y - cd[1])
                diff = min(x, y)
                diffs.append(diff)
            self.line_index = diffs.index(min(diffs))
            
            if self.line_index >= line_set_length: # >= as 0-indexed
                self.line_index -= line_set_length
            move_line(event)

        self.min_gap = 10
        
        def move_line(event):
            li = self.line_index
            line = line_set[li]
            c = self.canvas.coords(line)
            ci = self.canvas.coords(line_set_init[li])
            orient = li % 2 == 0
            # if orient and event.y >= ci[1]:
            #     self.canvas.coords(line, c[0], event.y, c[2], event.y)
            # elif not orient and event.x >= ci[0]:
            #     self.canvas.coords(line, event.x, c[1], event.x, c[3])
            print(event.y, self.canvas.coords(line_set[2]))
            match self.line_index:
                case 0 if (event.y >= ci[1] and
                           event.y < self.canvas.coords(line_set[2])[1] - self.min_gap):
                    self.canvas.coords(line, c[0], event.y, c[2], event.y)
                case 1 if (event.x <= ci[0] and
                           event.x > self.canvas.coords(line_set[3])[0] + self.min_gap):
                    self.canvas.coords(line, event.x, c[1], event.x, c[3])
                case 2 if (event.y <= ci[1] and
                           event.y > self.canvas.coords(line_set[0])[1] + self.min_gap):
                    self.canvas.coords(line, c[0], event.y, c[2], event.y)
                case 3 if (event.x >= ci[0] and
                           event.x < self.canvas.coords(line_set[1])[0] - self.min_gap):
                    self.canvas.coords(line, event.x, c[1], event.x, c[3])

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

        self.canvas.bind('<Button-1>', get_line)
        self.canvas.bind('<B1-Motion>', move_line)

    # scroll guillotine with bar
    def image_scale(self, root, img, factor):
        if factor == 0:
            # no pre-subsample filtering / downscale => aliasing
            scaled = img.subsample(self.sample)
        else:
            scaled = img.zoom(factor)
        self.canvas.itemconfigure(self.pdfview, image=scaled)
        self.canvas['scrollregion']=(0,0,scaled.width(),
                                        scaled.height())
        root.image = scaled # maintain reference w/o PIL
        return scaled

    def canvas_fit(self, img):
        self.canvas['width'] = img.width()   + (self.lt - self.bd) * 2
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
 
