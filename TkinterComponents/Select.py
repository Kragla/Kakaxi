from tkinter import Frame, Entry, Text, Listbox, StringVar, END, YES


class InputSelect(Frame):
    def __init__(self, window, ipt_width, items=None):
        self.window = window
        self.selections = items

        self.__init_input(ipt_width)
        self.__init_list_box()
        self.__init_area()

    def __init_input(self, ipt_width):
        self.ipt = Entry(self.window, width=ipt_width, bd=0, highlightthickness=0, foreground='#737373', font=("Consolas", 12))
        self.ipt.pack(fill="x", expand=YES, ipadx=5, ipady=10)
        string_var = StringVar()
        self.ipt.config(textvariable=string_var)
        self.string_var = string_var

        self.ipt.focus_set()

    
    def __init_list_box(self):
        self.lb = Listbox(self.window, borderwidth=0, font=('Consolas', 12))
        self.reload_items(self.selections)

    
    def __init_area(self):
        self.area = Text(self.window, height=10, highlightthickness=0, background="#333", foreground="yellow", font=('Consolas', 9))


    def reload_items(self, items):
        if self.lb.size() > 0:
            self.lb.delete(0, END)
        if items:
            for item in items:
                self.lb.insert(END, item)


    def set_ipt_value(self, value):
        self.string_var.set(value)
        self.ipt.icursor(END)

    
    def get_ipt_value(self):
        return self.string_var.get()


    def select_lb_item(self, index):
        self.lb.selection_clear(0, END)
        self.lb.selection_set(index)
        self.lb.see(index)

        
    def show_lb(self):
        if not self.lb.winfo_viewable():
            self.lb.pack(fill='both', expand=YES)
            self.lb.selection_set(0)

    
    def hide_lb(self):
        if self.lb.winfo_viewable():
            self.lb.pack_forget()
    

    def get_area_content(self):
        return self.area.get("1.0", END)
    

    def show_area(self, content):
        if not self.area.winfo_viewable():
            self.area.pack(fill="both", expand=YES, ipadx=5, ipady=10)
        if content:
            first_line = self.area.get("1.0", END)
            if first_line:
                self.area.delete("1.0", END)
            self.area.insert(END, content)
            
    
    def hide_area(self):
        if self.area.winfo_viewable():
            self.area.pack_forget()

