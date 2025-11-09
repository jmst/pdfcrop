from tkinter import Tk, Canvas, ttk
def setColor(new_color):
    global color
    color = new_color
    canvas.dtag('all', 'palette_selected')
    canvas.itemconfigure('palette', outline=bunsel)
    canvas.addtag('palette_selected', 'withtag', 'b_'+color)
    canvas.itemconfigure('palette_selected', outline=bsel)
    
def savePos(event):
    global lastx, lasty
    lastx, lasty = event.x, event.y
    
def addLine(event):
    canvas.create_line((lastx, lasty, event.x, event.y), fill=color,
                       tags = 'current_line', width=2)
    savePos(event)

def add_color(color, id):
    try:
        x0 = canvas.coords(id)[0] + bsize + bpad
    except:
        x0 = bx_init
    y0 = by_pos
    x1 = x0 + bsize
    y1 = y0 + bsize
    id = canvas.create_rectangle((x0, y0, x1, y1), fill=color,
                                 tags=['b_'+color, 'palette'],
                                 outline = bunsel)
    canvas.tag_bind('b_'+color, "<Button-1>", lambda x: setColor(color))
    return id

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

bx_init = 10
by_pos = 10
bsize = 20
bpad = 5
bunsel = '#000000'
bsel = '#999999'

h = ttk.Scrollbar(root, orient='horizontal')
v = ttk.Scrollbar(root, orient='vertical')
canvas = Canvas(root, width=360, height=240, scrollregion=(0,0,1000,1000),
                xscrollcommand=h.set, yscrollcommand=v.set)
h['command']=canvas.xview
v['command']=canvas.yview
canvas.grid(column=0, row=0, sticky='nswe')
h.grid(column=0, row=1, sticky='we')
v.grid(column=1, row=0, sticky='ns')

id = add_color('black', 1) # what if not first?
id = add_color('red', id)
add_color('blue', id)
canvas.itemconfigure('palette', width=3)
setColor('black')

# id = canvas.create_rectangle((id.x0+25, 10, id.x1+25, 30), fill='blue')
canvas.bind('<Button-1>', savePos)
canvas.bind('<B1-Motion>', addLine)
canvas.bind('<B1-ButtonRelease>', lambda e: canvas.itemconfigure('current_line', width=1))

root.mainloop()
