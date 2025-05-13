# view/polygon_view.py
import tkinter as tk
import math

class PolyView(tk.Tk):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter  # 接收演示者实例
        self.title("多边形游戏")  # 设置窗口标题
        self.geometry("800x600")  # 设置窗口初始大小
        self.resizable(True, True)  # 允许窗口大小可调整
        self.configure(background="#e3f2fd")
        self.canvas = tk.Canvas(self, width=600, height=400, bg="#fff9c4", bd=4, relief=tk.SOLID, highlightbackground="#ffd54f", highlightcolor="#ffd54f", highlightthickness=4, borderwidth=0)
        self.canvas.pack(padx=10, pady=10)  # 增加一些内边距
        self.status_label = tk.Label(self, text="游戏就绪", relief=tk.SUNKEN, anchor=tk.W, bg="#fff9c4", bd=1, highlightbackground="#ffd54f", highlightcolor="#ffd54f", highlightthickness=4, borderwidth=0)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.setup_ui()

    def setup_ui(self):
        # 创建控制面板，使用frame分隔布局
        control_frame = tk.Frame(self, bg="#e3f2fd")
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # 调整按钮的样式并居中
        button_frame = tk.Frame(control_frame, bg="#e3f2fd")
        button_frame.pack(side=tk.TOP, pady=10)

        # 定义按钮样式
        button_style = {
            'width': 10,
            'height': 2,
            'font': ("Arial", 12, "bold"),
            "bg": "#e3f2fd",
            "fg": "#1565c0",
            "bd": 2,
            "relief": tk.SOLID,
            "highlightbackground": "#90caf9",
            "highlightcolor": "#90caf9",
            "highlightthickness": 2
        }

        # 按钮的背景色和文字颜色
        buttons = [
            ("新游戏", self.presenter.new_game, "#4CAF50"),
            ("撤销", self.presenter.undo, "#f44336"),
            ("重做", self.presenter.redo, "#FFC107"),
            ("显示最优解", self.presenter.show_solution, "#2196F3"),
            ("历史记录", lambda: self.presenter.show_history(), "#9C27B0")
        ]

        for (text, command, bg_color) in buttons:
            button = tk.Button(button_frame, text=text, command=command, **button_style)
            button.pack(side=tk.LEFT, padx=10)
            button.bind("<Enter>", lambda event, b=button: b.config(bg="#f8bbd0", fg="#ffffff"))
            button.bind("<Leave>", lambda event, b=button: b.config(bg="#fce4ec", fg="#d81b60"))

        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_enter(self, button):
        button.config(bg="#bbdefb", fg="#ffffff", highlightbackground="#64b5f6", highlightcolor="#64b5f6")

    def on_leave(self, button):
        button.config(bg="#e3f2fd", fg="#1565c0", highlightbackground="#90caf9", highlightcolor="#90caf9")


    def draw_polygon(self, vertices, operators):
        # 保存到实例
        self.vertices = vertices
        self.operators = operators

        self.canvas.delete("all")
        n = len(vertices)

        if n == 1:
            x, y = 300, 200
            self.canvas.create_oval(x - 30, y - 30, x + 30, y + 30,
                                    fill="lightblue", outline="black", width=2)
            self.canvas.create_text(x, y, text=str(vertices[0]), font=("Arial", 16, "bold"))
            return

        if n == 2:
            x1, y1 = 200, 200
            x2, y2 = 400, 200
            self.canvas.create_line(x1, y1, x2, y2, tags="edge_0", width=2, fill="black")
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 - 20
            self.canvas.create_text(mid_x, mid_y, text=operators[0], tags="op_0", font=("Arial", 18, "bold"))  # 增大字体
            self.canvas.create_oval(x1 - 15, y1 - 15, x1 + 15, y1 + 15, fill="white", tags="vertex_0")
            self.canvas.create_text(x1, y1, text=str(vertices[0]))
            self.canvas.create_oval(x2 - 15, y2 - 15, x2 + 15, y2 + 15, fill="white", tags="vertex_1")
            self.canvas.create_text(x2, y2, text=str(vertices[1]))
            return

        center_x, center_y = 300, 200
        radius = 150 if n > 3 else 100
        points = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            self.canvas.create_line(x1, y1, x2, y2, tags=f"edge_{i}", width=2, fill="black")
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y, text=operators[i], tags=f"op_{i}", font=("Arial", 18, "bold"))  # 增大字体

        for i, (x, y) in enumerate(points):
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="white", tags=f"vertex_{i}")
            self.canvas.create_text(x, y, text=str(vertices[i]), tags=f"val_{i}")

    def show_toast(self, message):
        """显示提示消息"""
        self.status_label.config(text=message)
        # 如果是游戏结束的消息，使用更醒目的样式
        if "游戏结束" in message:
            self.status_label.config(fg="red", font=("Arial", 12, "bold"))
            # 5秒后恢复默认样式
            self.after(5000, lambda: self.status_label.config(
                text="游戏就绪",
                fg="black",
                font=("Arial", 10, "normal")
            ))
        else:
            # 其他消息2秒后消失
            self.after(2000, lambda: self.status_label.config(
                text="游戏就绪",
                fg="black",
                font=("Arial", 10, "normal")
            ))

    def on_canvas_click(self, event):
        closest = None
        min_dist = float('inf')
        if not hasattr(self, 'operators') or not self.operators:
            return  # 尚未绘制任何多边形
        print("点击检测，operators =", self.operators, "vertices =", self.vertices)
        # for i in range(len(self.presenter.model.operators)):
        for i in range(len(self.operators)):
            tag = f"edge_{i}"
            coords = self.canvas.coords(tag)
            if coords:
                x1, y1, x2, y2 = coords
                dist = self.point_to_line_distance(event.x, event.y, x1, y1, x2, y2)
                if dist < min_dist:
                    min_dist = dist
                    closest = i

        if closest is not None and min_dist < 10:
            self.presenter.on_edge_selected(closest)

    @staticmethod
    def point_to_line_distance(x, y, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)

        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return math.hypot(x - nearest_x, y - nearest_y)

    def show_history(self, mode='all'):
        from view.dialogs import HistoryDialog  # 延迟导入，避免循环导入
        HistoryDialog(self, self.presenter, mode)
