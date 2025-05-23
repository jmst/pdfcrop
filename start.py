from ctypes import windll
import tkinter as tk

# is this auto run on import?
windll.shcore.SetProcessDpiAwareness(2)

def start(func):
    root = tk.Tk()
    root.configure(bg='coral')
    # root.geometry('+-7+0')
    root.geometry('+0+0') # hc
    # ttk.Style().configure(".", background='magenta', foreground='black')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    obj = func(root)
    # root.attributes('-topmost', 1) # no diff, even multi windows return to bot of stack
    root.bind('<Control-w>', lambda _: root.destroy())
    root.mainloop()
    return obj

    # root.resizable(tk.FALSE, tk.FALSE)
    # print(root.tk.eval('wm stackorder '+str(root)))


if __name__ == "__main__":
    def nullfunc():
        return
    start(lambda *_: nullfunc)

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
