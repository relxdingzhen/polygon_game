# # from view.dialogs import *
# from dialogs import HistoryDialog
# import tkinter as tk
# from tkinter import ttk
#
# class AIHistoryDialog(HistoryDialog):
#     def __init__(self, parent, presenter, mode='all'):
#         super().__init__(parent, presenter, mode)
#         self.title("AI 对战 - 操作历史记录")
#         self.configure_background()
#         self.configure_widgets()
#
#     def configure_background(self):
#         # 创建一个画布用于绘制渐变背景
#         self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
#         self.canvas.pack(fill=tk.BOTH, expand=True)
#
#         # 定义渐变颜色
#         start_color = "#e3f2fd"
#         end_color = "#fff3e0"
#
#         # 绘制渐变背景
#         for i in range(self.winfo_screenheight()):
#             r = int(int(start_color[1:3], 16) + (
#                         int(end_color[1:3], 16) - int(start_color[1:3], 16)) * i / self.winfo_screenheight())
#             g = int(int(start_color[3:5], 16) + (
#                         int(end_color[3:5], 16) - int(start_color[3:5], 16)) * i / self.winfo_screenheight())
#             b = int(int(start_color[5:7], 16) + (
#                         int(end_color[5:7], 16) - int(start_color[5:7], 16)) * i / self.winfo_screenheight())
#             color = f"#{r:02x}{g:02x}{b:02x}"
#             self.canvas.create_line(0, i, self.winfo_screenwidth(), i, fill=color)
#
#     def configure_widgets(self):
#         # 配置按钮样式
#         style = ttk.Style()
#
#         # 默认状态
#         style.configure("TButton",
#                         background="#e3f2fd",
#                         borderwidth=2,
#                         relief="solid",
#                         bordercolor="#90caf9",
#                         foreground="#1565c0")
#
#         # 悬停状态
#         style.map("TButton",
#                   background=[('active', '#bbdefb')],
#                   bordercolor=[('active', '#64b5f6')],
#                   foreground=[('active', '#ffffff')])
#
#         # 配置输入/输出区域样式
#         self.text_area = tk.Text(self,
#                                  background="#fff9c4",
#                                  borderwidth=4,
#                                  relief="solid",
#                                  bordercolor="#ffd54f",
#                                  highlightthickness=0,
#                                  bd=0,
#                                  padx=10,
#                                  pady=10)
#         self.text_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
#         self.text_area.config(highlightbackground="#ffd54f", highlightcolor="#ffd54f", highlightthickness=4, bd=0)
#         self.text_area.bind("<Configure>", lambda e: self.text_area.configure(width=e.width, height=e.height))
#
#         # 模拟立体感
#         self.text_area.pack_propagate(0)
#         self.text_area.place(x=20, y=20, width=self.winfo_width() - 40, height=self.winfo_height() - 40)
#         shadow = tk.Frame(self, background="#f0f0f0")
#         shadow.place(x=24, y=24, width=self.winfo_width() - 40, height=self.winfo_height() - 40)
#
#     def format_step(self, step, step_num):
#         """重写格式化方式：突出显示AI/玩家行为等"""
#         content = f"步骤 {step_num}:\n"
#         actor = step.get("actor", "未知")  # 假设step里加了 'actor': 'AI' 或 'Player'
#         content += f"操作者: {actor}\n"
#         content += f"顶点数: {len(step['vertices'])}\n"
#
#         if 'merge_info' in step and step['merge_info']:
#             info = step['merge_info']
#             content += "┌── 合并详情 ──┐\n"
#             content += f"│ {info['indices'][0] + 1}号({info['values'][0]}) "
#             content += f"和 {info['indices'][1] + 1}号({info['values'][1]})\n"
#             content += f"│ 运算符: {info['operator']}\n"
#             content += f"│ 结果值: {info['result']}\n"
#             content += "└────────────┘\n"
#         else:
#             content += "状态类型: 初始配置\n"
#
#         content += f"当前顶点: {', '.join(map(str, step['vertices']))}\n"
#         if len(step['operators']) > 0:
#             content += f"剩余运算符: {' → '.join(step['operators'])}\n"
#
#         # AI 特有内容（比如信心值或路径）
#         if actor == 'AI' and 'ai_decision' in step:
#             decision = step['ai_decision']
#             content += f"AI 选择理由: {decision.get('reason', '未知')}\n"
#             content += f"评估值: {decision.get('score', 'N/A')}\n"
#
#         content += "━" * 40 + "\n"
#         return content
# from view.dialogs import *
from dialogs import HistoryDialog
import tkinter as tk
from tkinter import ttk

class AIHistoryDialog(HistoryDialog):
    def __init__(self, parent, presenter, mode='all'):
        super().__init__(parent, presenter, mode)
        self.title("AI 对战 - 操作历史记录")
        self.configure_background()
        self.configure_widgets()

    def configure_background(self):
        # 创建一个画布用于绘制渐变背景，使用与polygon_view.py相同的颜色
        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 定义渐变颜色，与polygon_view.py一致
        start_color = "#e3f2fd"
        end_color = "#fff9c4"

        # 绘制渐变背景
        for i in range(self.winfo_screenheight()):
            r = int(int(start_color[1:3], 16) + (
                        int(end_color[1:3], 16) - int(start_color[1:3], 16)) * i / self.winfo_screenheight())
            g = int(int(start_color[3:5], 16) + (
                        int(end_color[3:5], 16) - int(start_color[3:5], 16)) * i / self.winfo_screenheight())
            b = int(int(start_color[5:7], 16) + (
                        int(end_color[5:7], 16) - int(start_color[5:7], 16)) * i / self.winfo_screenheight())
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, self.winfo_screenwidth(), i, fill=color)

    def configure_widgets(self):
        # 配置按钮样式，与polygon_view.py一致
        style = ttk.Style()

        # 默认状态
        style.configure("TButton",
                        background="#e3f2fd",
                        borderwidth=2,
                        relief="solid",
                        bordercolor="#90caf9",
                        foreground="#1565c0")

        # 悬停状态
        style.map("TButton",
                  background=[('active', '#bbdefb'), ('hover', '#bbdefb')],
                  bordercolor=[('active', '#64b5f6'), ('hover', '#64b5f6')],
                  foreground=[('active', '#ffffff'), ('hover', '#ffffff')])

        # 配置输入/输出区域样式，使用与polygon_view.py相似的颜色
        self.text_area = tk.Text(self,
                                 background="#fff9c4",
                                 borderwidth=4,
                                 relief="solid",
                                 bordercolor="#ffd54f",
                                 highlightthickness=0,
                                 bd=0,
                                 padx=10,
                                 pady=10)
        self.text_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.text_area.config(highlightbackground="#ffd54f", highlightcolor="#ffd54f", highlightthickness=4, bd=0)
        self.text_area.bind("<Configure>", lambda e: self.text_area.configure(width=e.width, height=e.height))

        # 模拟立体感
        self.text_area.pack_propagate(0)
        self.text_area.place(x=20, y=20, width=self.winfo_width() - 40, height=self.winfo_height() - 40)
        shadow = tk.Frame(self, background="#f0f0f0")
        shadow.place(x=24, y=24, width=self.winfo_width() - 40, height=self.winfo_height() - 40)

    def format_step(self, step, step_num):
        """重写格式化方式：突出显示AI/玩家行为等"""
        content = f"步骤 {step_num}:\n"
        actor = step.get("actor", "未知")  # 假设step里加了 'actor': 'AI' 或 'Player'
        content += f"操作者: {actor}\n"
        content += f"顶点数: {len(step['vertices'])}\n"

        if 'merge_info' in step and step['merge_info']:
            info = step['merge_info']
            content += "┌── 合并详情 ──┐\n"
            content += f"│ {info['indices'][0] + 1}号({info['values'][0]}) "
            content += f"和 {info['indices'][1] + 1}号({info['values'][1]})\n"
            content += f"│ 运算符: {info['operator']}\n"
            content += f"│ 结果值: {info['result']}\n"
            content += "└────────────┘\n"
        else:
            content += "状态类型: 初始配置\n"

        content += f"当前顶点: {', '.join(map(str, step['vertices']))}\n"
        if len(step['operators']) > 0:
            content += f"剩余运算符: {' → '.join(step['operators'])}\n"

        # AI 特有内容（比如信心值或路径）
        if actor == 'AI' and 'ai_decision' in step:
            decision = step['ai_decision']
            content += f"AI 选择理由: {decision.get('reason', '未知')}\n"
            content += f"评估值: {decision.get('score', 'N/A')}\n"

        content += "━" * 40 + "\n"
        return content