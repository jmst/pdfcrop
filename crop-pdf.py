import os
import sys
import pymupdf
from pathlib import Path
from tkinter import Tk, StringVar

from gui import TkGui

root = Tk()
gui = TkGui(root)

# TkGui.

root.mainloop()

dir = os.getcwd()

# i_file = os.path.join(dir, input(f"Input file: {dir}\\"))
i_file = Path(dir, "houdini_foundations_19_5_01.pdf")

gui.addLabel("Path: ")
root.mainloop()

o_file = i_file.with_stem(i_file.stem + "_cropped")
print(o_file)

doc = pymupdf.open(i_file)

pgno = 0
pix = doc[pgno].get_pixmap(dpi=150)
pix.save("t-%s.png" % pgno)

# sys.exit()

# p = input("Page number >") - 1
p = 9 # 17-1
pp = 226 # p+1 # is a range so not right

# replace eg. or 40, with x
x0 = int(input("x0 > ") or 30) # spread inner
y0 = int(input("y0 > ") or 65)
xoff = int(input("x offset > ") or 60) # spread outer
yoff = int(input("y offset > ") or 40)

# line wrap => uneven appearing odd/even margins

#PROBLEM: altering inner for odd pages affects regular outer? maybe i can't think

for i in range (p, pp):
    print("Cropping", i)
    page = doc[i-1]
    x1 = page.rect.x1
    y1 = page.rect.y1
    if (i % 2 != 0):
        x0, xoff = xoff, x0
    page.set_cropbox(pymupdf.Rect(x0, y0, x1-xoff, y1-yoff))

doc.save(os.path.join(o_file))

# add pixel-wise coordinate selection gui
