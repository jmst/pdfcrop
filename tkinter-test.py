from tkinter import Tk, StringVar
from tkinter import ttk

class FeetToMeters:
    
    def __init__(self, root):
        
        root.title("Feet to Meters")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="nwes")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        #### widgets
        
        self.feet = StringVar()
        feet_entry = ttk.Entry(mainframe, width=7, textvariable=self.feet)
        feet_entry.grid(column=2, row=1, sticky="we")
        
        self.meters = StringVar()
        ttk.Label(mainframe, textvariable=self.meters).grid(column=2, row=2, sticky="we")
        
        self.metersInt = StringVar()
        ttk.Label(mainframe, textvariable=self.metersInt).grid(column=2, row=3, sticky="we")
        
        ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(
            column=3, row=4, sticky="w")
        
        #### geo grid
        
        ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky="w")
        ttk.Label(mainframe, text="is equivelant to").grid(column=1, row=2, sticky="e")
        ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky="w")
        ttk.Label(mainframe, text="integer").grid(column=3, row=3, sticky="w")
        
        for child in mainframe.winfo_children(): # padding
            child.grid_configure(padx=5, pady=5)
            
        feet_entry.focus()
        
        root.bind("<Return>", self.calculate)

    def calculate(self, *args):
        try:
            value = float(self.feet.get())
            m = ((0.3048 * value * 10000.0 + 0.5)/10000.0)
            self.meters.set(str(m))
            self.metersInt.set(str(int(m)))
        except ValueError:
            pass
        
#### binds

root = Tk()
FeetToMeters(root)
root.mainloop()
