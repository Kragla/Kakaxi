# Python 3.10
# PyAutoGUI   0.9.53 (pip install pyautogui)
# opencv    4.8.0.74 (pip install opencv-python)
# paramiko  3.3.1
# keyboard
# playwright        1.44.0

# # CPU 0.1%; MEM: 32MB
import keyboard
from tkinter import Tk, END, messagebox
from TkinterComponents.Select import InputSelect
import pyautogui
import cv2
import re
import sys
import time
from datetime import datetime
import os.path

from client.file_utils import find_files

# 调用windows api显示窗口
import ctypes
#import ctypes.wintypes

# 配置
CONFIDENCE = 0.8
from client.settings import ENCODING
from client.file_utils import get_abs_path
from client.settings import KAKAXISETTINGS
COMMAND_PATHS = KAKAXISETTINGS['commandPaths']
WINDOW_TITLE = KAKAXISETTINGS['windowTitle']
WINDOW_ICON = KAKAXISETTINGS['windowIcon']

pyautogui.PAUSE = 1 # 执行一些pyautogui动作后暂停的秒数; time.sleep
pyautogui.FAILSAFE = True # 鼠标移到左上角(0,0), 将抛出异常failSafeException(程序无法终止时这样操作从而终止程序)


def main():
    kakaxi = Kakaxi()
    # 显示窗体
    kakaxi.show()


class Kakaxi(object):
    def __init__(self):
        self.h_wnd = 0
        self.main_window = None
        self.scripts_dic = {}
        self.all_options = None

        self.timer = None
        self.last_pressed_key = None
        self.last_input_value = None

        self.selected_key = None
        self.selected_index = -1
        self.selected_content = None

        # 添加热键
        self.add_hotkey()

        # 主窗口
        self.main_window = Tk()
        self.main_window.title(WINDOW_TITLE)
        
        # self.key_combobox = ttk.Combobox(self.main_window, values=self.all_options, width=100)
        # self.key_combobox.grid(row=0, column=0, padx=10, pady=10, ipadx=40, ipady=0)
        # self.key_combobox.focus_set()  # 设置焦点到key_combobox

        self.key_combobox = InputSelect(self.main_window, 100)
        # 加载脚本数据
        self.load_scripts()
        # 给Entry绑定键盘输入事件
        self.key_combobox.ipt.bind('<KeyRelease>', lambda event: self.__ipt_change(event))
        self.key_combobox.ipt.bind('<Return>', lambda event: self.run())
        # 给Text绑定回车事件, 触发Entry的回车事件
        self.key_combobox.area.bind('<Return>', lambda event: self.run())
        

    def add_hotkey(self):
        # 窗体显示前, 注册全局热键, 否则会注册热键会失败
        def body_flicker():
            # taskbar_region = (0, 800, 1920, 880)
            # locate = pyautogui.locateOnScreen(WINDOW_ICON)
            print('body_flicker')
            
            user32 = ctypes.WinDLL('user32')
            if not self.h_wnd:
                self.h_wnd = user32.FindWindowW(None, WINDOW_TITLE)
                print('self.h_wnd', self.h_wnd)
            if self.main_window.wm_state() == 'iconic':
                if self.h_wnd == 0:
                    print('获取窗口失败')
                    return
                # SW_RESTORE
                user32.ShowWindow(self.h_wnd, 9)
            else:
                # SW_MINIMIZE
                user32.ShowWindow(self.h_wnd, 6)
  
        # keyboard.add_hotkey('ctrl+alt+space', body_flicker)
        keyboard.add_hotkey('ctrl+alt+8', body_flicker)


    # 加载所有配置
    def load_scripts(self):
        self.scripts_dic = {}
        self.extend_scripts_dic_from_files()
        self.all_options = list(self.scripts_dic.keys())
        self.key_combobox.reload_items(self.all_options)


    def extend_scripts_dic_from_files(self):
        for path in COMMAND_PATHS:
            all_files = find_files(path, exclude_strs=['.png','.jpg','.jpeg','.gif'])
            for file in all_files:
                file_name = os.path.basename(file)
                file_name, _ = os.path.splitext(file_name)
                with open(file, encoding=ENCODING) as f:
                    file_content = f.read()
                    if file_name.lower().startswith('title'):
                        key = file_name.replace('title', '', 1).strip()
                    else:
                        directory_name = os.path.basename(os.path.dirname(file))
                        key = f"{directory_name} - {file_name}"

                    script_type = 0
                    if file_content.startswith('###'):
                        # ###开头的文件包含多个命令, ###作为分隔符
                        for titleAndContent in file_content.split('###'):
                            if titleAndContent:
                                # 获取第一行作为标题的一部分
                                first_newline_index = titleAndContent.index('\n')
                                
                                subTitle = titleAndContent[0:first_newline_index].strip()
                                if subTitle.endswith('::'):
                                    subTitle = subTitle[:-2].strip()
                                    script_type = 1
                                sub_key = f"{key} - {subTitle}"
                                
                                subContent = titleAndContent[first_newline_index + 1:].strip()
                                
                                if titleAndContent:
                                    self.scripts_dic[sub_key] = ScriptInfo(subContent, script_type, file)
                    else:
                        # 复杂的GUI操作命令必须放到operatekeyboardandmouse目录下才会被识别
                        if '/operatekeyboardandmouse/' in file.lower():
                            script_type = 1
                        
                        self.scripts_dic[key] = ScriptInfo(file_content, script_type, file)


    def show(self):
        # def on_enter(event):
        #     text = event.widget.get()
            
        #     matches = self.all_options

        #     if len(text) > 0:
        #         keywords = text.split(' ')
        #         for keyword in keywords:
        #             if keyword:
        #                 matches =  [option for option in matches if keyword.lower() in option.lower()]

        #         self.key_combobox['values'] = matches
        #         # 生成一个鼠标左键单击事件(按钮 1 是左键，按钮 2 是中键，按钮 3 是右键), 右上角的位置(下拉框的下拉按钮)
        #         self.key_combobox.event_generate("<Button-1>", x=self.key_combobox.winfo_width() - 2, y=2)
        #     else:
        #         self.key_combobox['values'] = matches

        # self.key_combobox.bind('<Return>', on_enter) # <KeyRelease>

        # execute_btn = tkinter.Button(self.main_window, text="确定") # 参数"command=self.run"无法传递event参数
        # execute_btn.grid(row=0, column=1, padx=10, pady=10, ipadx=0, ipady=0)
        # # 绑定回车事件
        # execute_btn.bind("<Return>", self.run)
        # # 绑定单击事件
        # execute_btn.bind("<Button-1>", self.run)
        
        # 设置屏幕位置
        self.set_location()

        # 设置不透明度
        self.main_window.attributes("-alpha", 0.8)
        self.main_window.config(background='#000000')

        self.main_window.mainloop()


    def set_location(self):
        # 获取屏幕宽度和高度
        screen_width = self.main_window.winfo_screenwidth()

        # 计算窗口的宽度和高度, 计算前需要先调用update()方法更新窗口信息, 否则计算结果不正确
        self.main_window.update()
        window_width = self.main_window.winfo_width()

        # 计算窗口位置的 x 和 y 坐标
        x = (screen_width - window_width) // 2
        y = 35  # 距离屏幕顶部的距离
        win_position = f"+{x}+{y}"

        # 设置窗口位置(不设置尺寸, 让其宽高自适应)
        self.main_window.geometry(f"{win_position}")
    

    def __ipt_change(self, event):
        # 当前按下的键
        key = event.keysym
        self.last_pressed_key = key
        if (key == "Up" and self.key_combobox.lb.size() > 0):
            if self.key_combobox.lb.size() == 0:
                return
            self.on_ipt_up()
            return
        if (key == "Down" and self.key_combobox.lb.size() > 0):
            self.on_ipt_down()
            return

        # 获取当前输入框的值, 空则不处理
        input_val = event.widget.get()
        self.realtime_input_val = input_val

        if key == "Return":
            # 中文输入法回车时其实还是输入, 不希望执行run方法
            # 中文输入法回车时会触发这里代码, 不会触发Entry的回车事件, 所以将run方法放到Entry的回车事件中
            # self.run()
            return

        # value为空, 并且按键按的不是Backspace
        if not input_val and key != "BackSpace":
            return
        
        # 输入框没有改变
        if self.selected_key == input_val:
            return
        # 有新值, 需要更新last_input_value
        if not self.last_input_value or self.last_input_value != input_val:
            self.last_input_value = input_val
            # 只有在有新值的情况下才需要取消之前的定时器(针对出现了额外获取了多余的键值触发了事件就会错误的取消计时器导致输入了值却不进行过滤)
            if self.timer:
                self.key_combobox.ipt.after_cancel(self.timer)
            # value是新值则处理, 否则不处理
            self.last_input_value = input_val
            self.timer = self.key_combobox.ipt.after(500, lambda: self.__filter_selections(input_val))


    def on_ipt_up(self):
        current_indexes = self.key_combobox.lb.curselection()
        should_select_index = -1
        if len(current_indexes) > 0:
            current_index = current_indexes[0]
            self.key_combobox.lb.selection_clear(current_index)
            if current_index == 0:
                # 选中最后一个
                should_select_index = self.key_combobox.lb.size() - 1
            else:
                # 选中前一个
                should_select_index = current_index - 1
        else:
            # 选中最后一个python -m http.server 6699
            should_select_index = self.key_combobox.lb.size() - 1

        self.select_item(should_select_index)

    def on_ipt_down(self):
        current_indexes = self.key_combobox.lb.curselection()
        should_select_index = -1
        if len(current_indexes) > 0:
            current_index = current_indexes[0]
            self.key_combobox.lb.selection_clear(current_index)
            if current_index == self.key_combobox.lb.size() - 1:
                # 选中第一个
                should_select_index = 0
            else:
                # 选中后一个
                should_select_index = current_index + 1
        else:
            should_select_index = 0
        
        self.select_item(should_select_index)
    

    def __filter_selections(self, value):
        print(f'__filter_selections: {value}')
        
        matches = self.all_options
        if value:
            keywords = value.split(' ')
            for keyword in keywords:
                if keyword:
                    matches = [option for option in matches if keyword.lower() in option.lower()]
        
        self.key_combobox.reload_items(matches)
        if len(matches) > 0:
            self.key_combobox.show_lb()
        else:
            self.key_combobox.hide_lb()
            self.key_combobox.hide_area()
        
        lb_size = self.key_combobox.lb.size()
        
        if lb_size > 0:
            self.key_combobox.lb.config(height=lb_size)

        self.key_combobox.lb.config(height=min(20, self.key_combobox.lb.size()))
        
        # 选中第一个
        self.select_item(0)


    # 选中指定的listbox选项, 并显示对用的内容
    def select_item(self, selected_index):
        if self.key_combobox.lb.size() > 0:
            # 选择指定项
            self.key_combobox.select_lb_item(selected_index)
            
            # 记录被选项
            self.selected_key = self.key_combobox.lb.selection_get()
            
            # 更新Entry
            if self.last_pressed_key in ['Up', 'Down']:
                self.key_combobox.set_ipt_value(self.selected_key)

            # 记录被选项的索引和值/实际内容
            self.selected_index = selected_index
            self.selected_content = self.scripts_dic.get(self.selected_key).script_content

            # 显示所选择对应的值
            self.key_combobox.show_area(self.selected_content)
        else:
            self.selected_key = self.key_combobox.get_ipt_value()
            self.selected_index = -1
            self.selected_content = ''


    def run(self):
        if len(self.key_combobox.lb.curselection()) == 0 and self.selected_index > -1:
            self.key_combobox.lb.selection_set(self.selected_index)

        if not self.selected_key:
            return
        if self.last_input_value == 'reload':
            self.load_scripts()
            messagebox.showinfo('提示', '已重新加载配置')
            return
        
        # self.key_combobox.set_ipt_value(self.selected_key)
        content = self.key_combobox.get_area_content()
        self.selected_content = content

        script_info = self.scripts_dic.get(self.selected_key)
        if script_info is None:
            messagebox.showerror('无效的选择', self.selected_key)
            return
        if self.selected_content:
            script_info.script_content = self.selected_content

        # **切换窗口**
        pyautogui.hotkey('alt', 'tab')

        # 最小化后, 热键呼出窗体才会在屏幕最上层显示; 否则它已经处于显示状态(只是在别的窗体下方), 热键呼出是没有反应的, 不会处于最顶层
        self.main_window.iconify()

        if script_info.script_type == 0:
            self.write_content(script_info.script_content)
        elif script_info.script_type == 1:
            self.operate_keyboard_and_mouse(script_info.script_file, script_info.script_content)
        else:
            messagebox.showerror('无效的命令类型', str(script_info.script_type))
        
        self.key_combobox.ipt.focus_set()
        

    def write_content(self, text):
        # 将内容添加到剪贴板再粘贴
        self.main_window.clipboard_clear()
        self.main_window.clipboard_append(text.rstrip()) # 去除末尾的换行, 避免命令行直接执行

        # 数字键盘开启时(无法触发shift+insert)先关闭小键盘
        if (self.is_num_lock_on()):
            keyboard.press_and_release('num lock')
        pyautogui.hotkey('shift', 'insert')

    
    def is_num_lock_on(self):
        # 使用ctypes调用windows操作系统API获取键盘状态
        # 获取键盘状态
        key_state = ctypes.windll.user32.GetKeyState(0x90)  # 0x90代表Num Lock键的虚拟键码

        # 检查最高位是否被设置，表示Num Lock是否开启
        return key_state & 1 == 1

    
    def operate_keyboard_and_mouse(self, script_file, script_content=None):
        if not script_content:
            with open(script_file, encoding=ENCODING) as f:
                script_content = f.read()
        
        cmds = [line for line in script_content.split("\n") if line.strip() and not line.strip().startswith("#")]
        
        cmds_block = []
        cmd_index = 0
        cmds_len = len(cmds)
        while True:
            # 读取命令; 注意这个代码块中, 命令索引指向的使当前执行的命令或者当前执行的命令块的最后一个命令
            if cmd_index >= cmds_len:
                break
            cmd = cmds[cmd_index].strip()
            print('cmd line: ', cmd)
            #do
            #    dragRel >>> position >>> -100 >>> 0
            #    moveRel >>> position >>> 100 >>> 0
            #while img_show qtscrcpy_title.png max_loop_count 10 frequency 1 action moveTo
            
            loop_count = 1
            do_while_match = None
            img_stop_signal = ''
            wait_seconds = 0.1
            action_after_img_showed = ''

            if cmd == "do" or cmd == "do:":
                while True:
                    # 索引移动到下一行, 读取下一行命令
                    cmd_index += 1
                    if cmd_index >= cmds_len:
                        break
                    cmd = cmds[cmd_index].strip()
                    
                    if 'while ' in cmd:
                        # 命令块已经获取完毕
                        pattern = r'\s*while(\s+img_show\s+(?P<stop_signal>.*?)){0,1}\s+max_loop_count\s+(?P<count>\d+)\s+frequency\s+(?P<wait_seconds>\d+)(\s+action\s+(?P<action>\w+)){0,1}'
                        do_while_match = re.match(pattern, cmd)
                        if do_while_match:
                            loop_count = int(do_while_match.group('count'))
                            wait_seconds = float('0.1' if not do_while_match.group('wait_seconds') else do_while_match.group('wait_seconds'))
                            img_stop_signal = do_while_match.group('stop_signal')
                            action_after_img_showed = do_while_match.group('action')
                            print(f'do..while..: 最多循环{loop_count}次, 执行命令等待{wait_seconds}秒后, 查看"{img_stop_signal}"是否存在, 若存在则对它执行命令: {action_after_img_showed}')
                        elif 'loop:' in cmd:
                            print(f'命令匹配loop规则失败: "{cmd}"')
                        break
                    else:
                        cmds_block.append(cmd)
            elif cmd.startswith("if"):
                while True:
                    # 索引移动到下一行, 读取下一行命令
                    cmd_index += 1
                    if cmd_index >= cmds_len:
                        break
                    cmd = cmds[cmd_index].strip()

                    if 'endif' in cmd:
                        # 命令块已经获取完毕
                        break
                    else:
                        cmds_block.append(cmd)
                pattern = r'\s*if\s+img\s+(?P<searched_img>.*)'
                if_match = re.match(pattern, cmd)
                searched_img_position = self.get_img_abs_path_and_find_position(if_match.group('searched_img'), script_file)
                print(f'处理if命令块, searched_img: {searched_img_position}')
                if not if_match and searched_img_position:
                    # 条件不符合, 则不执行命令块
                    cmds_block = []
                    continue
            else:
                cmds_block.append(cmd)
            
            for i in range(loop_count):
                # 执行一系列命令, 尝试使img_stop_signal出现;
                for cmd_item in cmds_block:
                    self.execute_cmd(cmd_item, script_file)
                
                # 检查img_stop_signal是否已经出现
                if do_while_match and img_stop_signal:
                    time.sleep(wait_seconds)
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f'img_stop_signal[{img_stop_signal}]不为空, 已等待{wait_seconds}秒, 尝试去查找它 第{i+1}次')
                    img_position = self.get_img_abs_path_and_find_position(img_stop_signal, script_file)
                    if img_position:
                        print(f'尝试{i+1}/{loop_count}次成功找到图片: {img_stop_signal}; 检查对图片进行的操作命令: [{action_after_img_showed}]')
                        self.execute_cmd(f'{action_after_img_showed} >>> position >>> {img_position[0]} >>> {img_position[1]}', script_file)
                        break
                
                print()

            # 命令或者命令块已经执行完毕
            cmds_block = []
            
            # 准备执行下一条命令
            cmd_index += 1
            
            print()
        
        # 脚本中所有命令全部完成
        messagebox.showinfo('success', '全部命令已执行完毕')
    

    def execute_cmd(self, cmd, script_file):
        print('execute_cmd:', cmd)
        cmd = cmd.strip()
        parts = [part.strip() for part in cmd.split(">>>") if part.strip()]
        if len(parts) > 0:
            cmd_name = parts[0].lower().strip()
            params_count = len(parts) - 1
            args = parts[1:]
            if cmd_name.startswith("click"):
                click_count_str = cmd_name.replace('click', '')
                click_count = int(click_count_str) if click_count_str else 0
                if params_count == 0:
                    # 鼠标在当前位置单击
                    self.mouse_click_position(click_count, None, None)
                elif args[0] == "position":
                    # 鼠标在指定位置单击
                    self.mouse_click_position(click_count, int(args[1]), int(args[2]))
                elif args[0] == "img":
                    # 鼠标单击指定图片, 参数1是图片路径
                    target = args[1]
                    img_position = self.get_img_abs_path_and_find_position(target, script_file)
                    self.mouse_click_position(click_count, img_position[0], img_position[1])
                else:
                    print(f'Click not implement: {cmd}')
                    return
            elif cmd_name.startswith("move") or cmd_name.startswith("drag"):
                target = args[0]
                mouse_operation = None
                if cmd_name.startswith("move"):
                    mouse_operation = pyautogui.moveTo if cmd_name == "moveto" else pyautogui.moveRel
                else:
                    mouse_operation = pyautogui.dragTo if cmd_name == "dragto" else pyautogui.dragRel
                
                if target == "position":
                    x_val = int(args[1])
                    y_val = int(args[2])
                    mouse_operation(x_val, y_val)
                elif target == "img":
                    img_path = args[1]
                    img_position = self.get_img_abs_path_and_find_position(img_path, script_file)
                    mouse_operation(img_position[0], img_position[1])
            elif cmd_name == "press":
                for key in args:
                    print('press', key)
                    pyautogui.press(key)
            elif cmd_name == "hotkey":
                # 键盘
                # 提取参数(除第一个元素外的其他元素)
                pyautogui.hotkey(*args)
            elif cmd_name == "input":
                # 输入
                input_content = cmd.replace('input ', '', 1).strip()
                self.write_content(input_content)
            elif cmd_name == "sleep":
                # 等待
                time.sleep(int(args[0]))
            else:
                print(f'Not implement command: {cmd}')
                return


    def mouse_click_position(self, click_count, click_x, click_y):
        if click_count == 0:
            pyautogui.click(click_x, click_y)
        elif click_count == 2:
            pyautogui.doubleClick(click_x, click_y)
    

    # 找到指定图片的位置(如果指定图片的路径是相对路径, 那么需要传一个同级目录下的其他文件的绝对路径)
    def get_img_abs_path_and_find_position(self, target, sibliing_file = None):
        abs_path = get_abs_path(target, sibliing_file) if sibliing_file else target
        target_position = self.find_a_image(abs_path)
        
        print(f'target_position: {target_position}')
        return target_position


    def hide_window(self, before_window_hidden):
        # **切换窗口**
        pyautogui.hotkey('alt', 'tab')
        
        if before_window_hidden:
            before_window_hidden()

        # 最小化后, 热键呼出窗体才会在屏幕最上层显示; 否则它已经处于显示状态(只是在别的窗体下方), 热键呼出是没有反应的, 不会处于最顶层
        self.main_window.iconify()


    def show_main_window(self):
        (click_x, click_y) = self.find_a_image(WINDOW_ICON)

        # 鼠标此时的位置
        origin_x, origin_y = pyautogui.position()

        # 鼠标点击图标
        pyautogui.click(click_x, click_y)

        # 还原鼠标位置
        pyautogui.moveTo(origin_x, origin_y)

        return True
    

    # 使用opencv查找图片位置, 和使用pyautogui.locateCenterOnScreen("图片路径", confidence=0.8)的效果一样(也需要安装opencv)
    def find_a_image(self, searchedImg) -> tuple | None:
        print(f'查找图片: {searchedImg}')
        screenshot = pyautogui.screenshot()
        screen_img_path = 'screenshot.png'
        screenshot.save(screen_img_path)
        screen_img = cv2.imread(screen_img_path)
        icon_img = cv2.imread(searchedImg)

        # 在图像screen_img中搜索指定模板icon_img(要搜索的图片), 匹配方法使用"归一化相关系数匹配"(TM_CCOEFF_NORMED);
        # 返回匹配结果result(二维数组), 可以理解为匹配结果图像的所有点的匹配值(这里匹配方法是TM_CCOEFF_NORMED所以越大越匹配)和点的位置坐标
        result = cv2.matchTemplate(screen_img, icon_img, cv2.TM_CCOEFF_NORMED)

        # 找到匹配结果result中的最小值, 最大值, 最小值坐标, 最大值坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f'匹配结果: max_val={max_val}; max_loc={max_loc}')
        # TM_CCOEFF_NORMED方法匹配结果值越大越匹配, 小与CONFIDENCE(例如0.8)认为不匹配
        if max_val < CONFIDENCE:
            print(f'没有找到图片: {searchedImg}')
            return None

        # 获取result上面使用的匹配方法是cv2.TM_CCOEFF_NORMED, 值越大表示越匹配, 所以我们需要最大值(对应的坐标(左上角坐标))
        icon_location = max_loc

        # 搜索的图片宽和高
        icon_width, icon_height = icon_img.shape[:-1]
        position_x = icon_location[0] + icon_width // 2
        position_y = icon_location[1] + icon_height // 2
        return (position_x, position_y)


class ScriptInfo(object):
    def __init__(self, script_content, script_type = 0, script_file = '') -> None:
        self.script_content = script_content
        self.script_type = script_type
        self.script_file = script_file


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 3 and args[1] == '-f':
        script_file = args[2]
        Kakaxi().operate_keyboard_and_mouse(script_file)
    else:
        main()
    