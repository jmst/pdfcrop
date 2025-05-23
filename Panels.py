import tkinter as tk
from tkinter import ttk
from _tkinter import TclError

from tkinter import filedialog as fd

from pdfcanvas import PdfCanvas
import start

class MenuBar:
    # self not necessary?
    def __init__(self, root):
        root.option_add('*tearOff', False)
        menubar = tk.Menu(root)
        root['menu'] = menubar
        menu_file = tk.Menu(root)
        menubar.add_cascade(label='File', menu=menu_file)
        menu_file.add_command(label='Open...', command = fd.askopenfilename)
        menu_file.add_command(label='Save',
                              command = lambda: print('save PLACEHOLDER'))
        menu_file.add_command(label='Save As...',command = fd.asksaveasfilename)
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
        menu_help.entryconfigure('email@test', state=tk.DISABLED) # copy symbol
        # menubar = tk.Menu(root).add_separator
        # menubar.add_command(label="C:/Users/James/Desktop/projects/code/py/pdfcrop/cropped.pdf", state = tk.DISABLED)

class LineSpinBox:
    def __init__(self, master, line_matrix = [None] * 4, sample = None,
                 canvas_lines = None, pref_pixel_ref = True):
        self.master = master
        self.canvas_lines = canvas_lines
        self.line_matrix = line_matrix # ! for conv
        self.sample = sample # self.img['sample']
        """init just sample, for conv otherwise nest lambda as func in try_get?"""
        self.pref_pixel_ref = pref_pixel_ref

        print(line_matrix)
        for i, ln in enumerate(list(line_matrix)):
            print(i, ln)
            box = ttk.Spinbox(master, state=tk.DISABLED)
            line_matrix[ln]['spinbox'] = box
            box.grid(row=i)
            self.init_spinbox(box, ln)

    def init_spinbox(self, box, ln):
            # def init_spinbox(self, ln):
            lm = self.line_matrix[ln]

            def try_get(txtvar, func, i):
                try:
                    # txtvar.set(func(txtvar.get(), ln))
                    txtvar.set(func(i, ln))
                # empty field -> expected floating-point number but got ""
                except TclError: # as e:
                    # print(e)
                    return

            # lm['txtvar/trace'] for removing trace later, unfinished
            if self.pref_pixel_ref:
                inc = 1
                limit = self.line_matrix[ln[0] + '1']['ogpos'] \
                    - self.line_matrix[ln[0] + '1']['conv']
                lm['txtvar'] = txtvar = tk.IntVar(self.root,
                                                  lm['pos'].get() - lm['conv'])
                lm['trace'] =txtvar.trace_add(
                    "write", lambda *_: try_get(txtvar, self.move_spinbox_conv))
            else:
                inc = self.sample # self.img['sample']
                limit = self.line_matrix[ln[0] + '1']['unconv'].get()
                txtvar = lm['unconv'] # self.unconv(lm) # lm['txtvar'] =
                proxy = lm['pos']
                # lm['trace'] = txtvar.trace_add("write", lambda *_: try_get(txtvar, self.move_spinbox_unconv))
                lm['trace'] = proxy.trace_add(
                    "write", lambda *_: try_get(txtvar,
                                                self.move_spinbox_unconv,
                                                proxy.get()))

            def pre_valid(i):
                if i.isdigit():
                    return i
                else:
                    return False
                    # errmsg.set("no")
            """pre-validation check if user typed integer"""
            vcmd = (self.master.register(pre_valid), '%P')

            box.config(increment=inc, from_=0, to=limit,
                           textvariable=txtvar,
                           validate = 'key', validatecommand=vcmd)
                           # command=lambda: self.move_line_spinbox(lm['pos'].get(), ln))
            box['state']=tk.NORMAL
            return box


    def conv(self, i, line):
        """Converts from unscaled value to scaled (I think)"""
        i = (i / self.sample
             + self.line_matrix[line]['conv'])
        return i

    # todo make these @classmethod?
    def move_spinbox_unconv(self, i, line):
        # self.move_spinbox(j, line)
        i = self.canvas_lines.unconv(i, self.line_matrix[line]['conv'],
                                     self.sample)
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
        #  self.line_matrix[line[0] + '0']['conv']
        self.canvas_lines.move_line(i, line = line)

if __name__ == "__main__":
    def main(root: tk.Tk):
        MenuBar(root)
        root2 = tk.Tk()
        sbox = LineSpinBox(root2)
    start.start(main)
