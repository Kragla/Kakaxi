import tkinter as tk

root = tk.Tk()

def add_item():
    item = entry.get()
    listbox.insert(tk.END, item)
    root.update()

entry = tk.Entry(root)
entry.pack()

listbox = tk.Listbox(root)
listbox.pack(fill='both', expand=True)

button = tk.Button(root, text="添加", command=add_item)
button.pack()

# 将窗口的位置设置为居中靠屏幕上方
root.wm_attributes('-topmost', 1)
root.geometry('+0+0')
root.mainloop()
