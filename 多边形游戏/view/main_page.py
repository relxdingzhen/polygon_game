import tkinter as tk
from tkinter import messagebox


class MainPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("主菜单")
        self.geometry("400x400")
        self.resizable(False, False)

        # 设置主背景渐变色
        self.configure(background="#e3f2fd")
        # 创建主框架
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 设置主背景渐变色 - 使用Canvas但不覆盖整个窗口
        self.setup_gradient()

        # 创建UI元素
        self.setup_ui()

    def setup_gradient(self):
        # 创建渐变背景
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # 绘制渐变
        for i in range(400):
            r1 = int(227 + (255 - 227) * i / 400)
            g1 = int(242 + (243 - 242) * i / 400)
            b1 = int(253 + (224 - 253) * i / 400)
            color = f"#{r1:02x}{g1:02x}{b1:02x}"
            self.canvas.create_line(0, i, 400, i, fill=color)

    def setup_ui(self):
        # 创建半透明遮罩框架，确保UI元素可见
        ui_frame = tk.Frame(self.main_frame, bg="#e3f2fd", bd=0)
        ui_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 创建标题
        title_label = tk.Label(ui_frame, text="欢迎来到多边形游戏",
                               font=("Arial", 16, "bold"), bg="#1565c0")
        title_label.pack(pady=30)

        # 创建按钮样式
        button_style = {
            "width": 20,
            "height": 2,
            "font": ("Arial", 12, "bold"),
            "bg": "#e3f2fd",
            "fg": "#1565c0",
            "bd": 2,
            "relief": tk.SOLID,
            "highlightbackground": "#90caf9",
            "highlightcolor": "#90caf9",
            "highlightthickness": 2
        }

        # 创建按钮
        buttons = [
            ("开始游戏", self.start_game),
            ("多人联机", self.start_multiplayer),
            ("AI人机对抗", self.start_aivs_human),
            ("退出游戏", self.quit_game)
        ]

        # 使用pack布局按钮
        for text, command in buttons:
            button = tk.Button(ui_frame, text=text, command=command, **button_style)
            button.pack(pady=10, padx=50, fill=tk.X)
            button.bind("<Enter>", lambda event, btn=button: self.on_enter(btn))
            button.bind("<Leave>", lambda event, btn=button: self.on_leave(btn))

    def on_enter(self, button):
        button.config(bg="#bbdefb", fg="#ffffff", highlightbackground="#64b5f6", highlightcolor="#64b5f6")

    def on_leave(self, button):
        button.config(bg="#e3f2fd", fg="#1565c0", highlightbackground="#90caf9", highlightcolor="#90caf9")

    def start_game(self):
        self.destroy()
        from presenter.polygon_presenter import PolyPresenter
        from view.polygon_view import PolyView

        presenter = PolyPresenter()
        view = PolyView(presenter)

    def start_multiplayer(self):
        from view.multiplayer_page import MultiplayerPage
        from presenter.multiplayer_presenter import MultiplayerPresenter
        self.destroy()
        page = MultiplayerPage()
        presenter = MultiplayerPresenter(page)
        page.mainloop()

    def start_aivs_human(self):
        from view.aivs_human_page import AIVsHumanPage
        self.destroy()
        ai_vs_human_page = AIVsHumanPage()
        ai_vs_human_page.mainloop()

    def quit_game(self):
        self.quit()

