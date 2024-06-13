from tkinter import Frame, Entry, Listbox, StringVar, END, YES


WIN_MIN_HEIGHT = 40
class InputSelect(Frame):
    def __init__(self, caller, parent, items, ipt_width):
        self.caller = caller
        self.parent = parent
        self.selections = items
        self.timer = None
        self.last_input_value = None
        self.last_pressed_key = None

        self.__init_input(ipt_width)
        w = self.ipt.winfo_width()
        h = self.ipt.winfo_height()
        self.__init_list_box()

    def __init_input(self, ipt_width):
        self.ipt = Entry(self.parent, width=ipt_width, bd=0, relief="sunken", highlightthickness=0, font=("Consolas", 12))
        self.ipt.pack(fill="x", expand=YES, ipadx=5, ipady=10)
        string_var = StringVar()
        self.ipt.config(textvariable=string_var)
        self.string_var = string_var

        # 给input绑定键盘输入事件
        self.ipt.bind('<KeyRelease>', lambda event: self.__ipt_change(event))
        self.ipt.focus_set()

    def set_ipt_value(self, value):
        self.string_var.set(value)
        self.ipt.icursor(END)

    def __ipt_change(self, event):
        # 当前按下的键
        key = event.keysym
        self.last_pressed_key = key
        if (key == "Up" and self.lb.size() > 0):
            if self.lb.size() == 0:
                return
            self.on_ipt_up()
            self.set_ipt_value(self.lb.selection_get())
            return
        if (key == "Down" and self.lb.size() > 0):
            self.on_ipt_down()
            self.set_ipt_value(self.lb.selection_get())
            return

        # 获取当前输入框的值, 空则不处理
        value = event.widget.get()

        if key == "Return":
            selected_txt = self.lb.selection_get()
            if selected_txt:
                self.set_ipt_value(selected_txt)
                if self.caller:
                    self.caller.run(selected_txt)
            return

        # value为空, 并且按键按的不是Backspace
        if not value and key != "BackSpace":
            return
        # 有新值, 需要更新last_input_value
        if not self.last_input_value or self.last_input_value != value:
            self.last_input_value = value
            # 只有在有新值的情况下才需要取消之前的定时器(针对出现了额外获取了多余的键值触发了事件就会错误的取消计时器导致输入了值却不进行过滤)
            if self.timer:
                self.ipt.after_cancel(self.timer)
            # value是新值则处理, 否则不处理
            self.last_input_value = value
            self.timer = self.ipt.after(500, lambda: self.__filter_selections(value))


    def on_ipt_up(self):
        current_indexes = self.lb.curselection()
        should_select_index = -1
        if len(current_indexes) > 0:
            current_index = current_indexes[0]
            self.lb.selection_clear(current_index)
            if current_index == 0:
                # 选中最后一个
                should_select_index = self.lb.size() - 1
            else:
                # 选中前一个
                should_select_index = current_index - 1
        else:
            # 选中最后一个
            should_select_index = self.lb.size() - 1

        self.select_lb_item(should_select_index)

    def on_ipt_down(self):
        current_indexes = self.lb.curselection()
        should_select_index = -1
        if len(current_indexes) > 0:
            current_index = current_indexes[0]
            self.lb.selection_clear(current_index)
            if current_index == self.lb.size() - 1:
                # 选中第一个
                should_select_index = 0
            else:
                # 选中后一个
                should_select_index = current_index + 1
        else:
            should_select_index = 0
        
        self.select_lb_item(should_select_index)
    
    def select_lb_item(self, index):
        self.lb.selection_set(index)
        self.lb.see(index)

    def __filter_selections(self, value):
        print(f'__filter_selections: {value}')
        self.lb.delete(0, END)
        
        matches = self.selections
        if value:
            keywords = value.split(' ')
            for keyword in keywords:
                if keyword:
                    matches =  [option for option in matches if keyword.lower() in option.lower()]
        
        if len(matches) > 0:
            for item in matches:
                self.lb.insert(END, item)
            self.__show_lb()
        else:
            self.__hide_lb()
        
        lb_size = self.lb.size()
        
        height = WIN_MIN_HEIGHT
        if lb_size > 0:
            self.lb.config(height=lb_size)
            height = lb_size * 18 + 40

        win_width = self.parent.winfo_width()
        win_x = self.parent.winfo_x()
        win_y = self.parent.winfo_y()
        geometry = '%dx%d+%d+%d' % (win_width, min(height, 18 * 20), win_x, win_y)
        self.parent.geometry(geometry)
        self.lb.config(height=self.lb.size())
        
        # 选中第一个
        self.lb.selection_clear(0, END)
        self.select_lb_item(0)
        if self.lb.size() > 0:
            self.lb.selection_set(0)
    
    def __init_list_box(self):
        self.lb = Listbox(self.parent, borderwidth=0, font=('Consolas', 12))
        
        for item in self.selections:
            self.lb.insert(END, item)
        
        self.__show_lb()
        
    def __show_lb(self):
        if not self.lb.winfo_viewable():
            self.lb.pack(fill='both', expand=YES)
            self.lb.selection_set(0)
    
    def __hide_lb(self):
        if self.lb.winfo_viewable():
            self.lb.pack_forget()

