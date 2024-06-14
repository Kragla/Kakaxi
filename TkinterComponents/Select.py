from tkinter import Frame, Entry, Listbox, StringVar, END, YES


class InputSelect(Frame):
    def __init__(self, window, items, ipt_width):
        self.window = window
        self.selections = items

        self.__init_input(ipt_width)
        self.__init_list_box()

    def __init_input(self, ipt_width):
        self.ipt = Entry(self.window, width=ipt_width, bd=0, highlightthickness=0, font=("Consolas", 12))
        self.ipt.pack(fill="x", expand=YES, ipadx=5, ipady=10)
        string_var = StringVar()
        self.ipt.config(textvariable=string_var)
        self.string_var = string_var

        self.ipt.focus_set()

    
    def __init_list_box(self):
        self.lb = Listbox(self.window, borderwidth=0, font=('Consolas', 12))
        
        for item in self.selections:
            self.lb.insert(END, item)
        
        self.show_lb()


    def set_ipt_value(self, value):
        self.string_var.set(value)
        self.ipt.icursor(END)


    def select_lb_item(self, index):
        self.lb.selection_set(index)
        self.lb.see(index)

        
    def show_lb(self):
        if not self.lb.winfo_viewable():
            self.lb.pack(fill='both', expand=YES)
            self.lb.selection_set(0)
    
    def hide_lb(self):
        if self.lb.winfo_viewable():
            self.lb.pack_forget()

