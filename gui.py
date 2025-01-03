from tkinter import Tk, StringVar
from tkinter import ttk

class TkGui:
    
    def __init__(self, root):
        self.controlidx = 0
        
        root.title("pdfcrop")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        mainframe=ttk.Frame(root)
        mainframe.grid(sticky="NSEW")
        mainframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=0)
        mainframe.rowconfigure(0, weight=0)
        mainframe.rowconfigure(1, weight=1)

        ttk.Style().configure("Danger.TFrame", background="red")
        ttk.Style().configure("ok.TFrame", background="blue")

        top_frame=ttk.Frame(mainframe, style="Danger.TFrame")
        top_frame.grid(row=0, sticky="we", columnspan=2)
        top_frame.columnconfigure(0, weight=0)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(1, weight=0)
        ttk.Label(top_frame, text="File: ", background="red").grid(column=0, row=0)
        ttk.Entry(top_frame, background="red").grid(column=1, row=0, sticky="we")
        
        ui_frame=ttk.Frame(mainframe, borderwidth=20, relief="ridge", style="Danger.TFrame",
                           width=100, height=100)
        ui_frame.grid(column=0, row=1, ipadx="5", sticky="nsew")
        ui_frame.columnconfigure(0, weight=1)
        ui_frame.rowconfigure(0, weight=1)
        ui_frame.rowconfigure(1, weight=1)

        input_frame=ttk.Frame(ui_frame, width=30, height=10)
        zoom_frame=ttk.Frame(ui_frame, style="ok.TFrame")
        input_frame.grid(column=0, row=0)
        zoom_frame.grid(column=0, row=1, sticky="nsew")
        
        im_frame=ttk.Frame(mainframe, borderwidth=5, relief="ridge",
                          width=200, height=282.85).grid(column=1, row=1, sticky="e")

    # def addLabel(self, txt):
    #     ttk.Label(mainframe, text=txt, background="red"
    #               ).grid(column=0, row=self.controlidx)
    #     self.controlidx += 1

# if __name__ == "__main__":
root = Tk()
TkGui(root)
root.mainloop()
