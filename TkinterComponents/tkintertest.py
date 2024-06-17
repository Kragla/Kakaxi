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

area = tk.Text(root, height=10)
area.pack()
area.after(3000, lambda: area.pack())

lable = tk.Label(root, text="这是一个标签")
lable.pack()
lable.after(2000, lambda: area.pack_forget())

# 将窗口的位置设置为居中靠屏幕上方
root.wm_attributes('-topmost', 1)
root.geometry('+0+0')
root.mainloop()
