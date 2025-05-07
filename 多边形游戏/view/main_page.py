import tkinter as tk
from tkinter import messagebox


class MainPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("主菜单")  # 设置主菜单窗口的标题
        self.geometry("400x400")  # 设置窗口大小
        self.resizable(False, False)  # 不允许调整窗口大小

        self.setup_ui()

    def setup_ui(self):
        # 主菜单的标题
        title_label = tk.Label(self, text="欢迎来到多边形游戏", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # 开始游戏按钮
        start_button = tk.Button(self, text="开始游戏", width=20, height=2, command=self.start_game, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        start_button.pack(pady=10)

        # 多人联机按钮
        multiplayer_button = tk.Button(self, text="多人联机", width=20, height=2, command=self.start_multiplayer, bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
        multiplayer_button.pack(pady=10)

        # AI人机对抗按钮
        ai_vs_human_button = tk.Button(self, text="AI人机对抗", width=20, height=2, command=self.start_aivs_human, bg="#FF9800", fg="white", font=("Arial", 12, "bold"))
        ai_vs_human_button.pack(pady=10)

        # 退出按钮
        quit_button = tk.Button(self, text="退出游戏", width=20, height=2, command=self.quit_game, bg="#f44336", fg="white", font=("Arial", 12, "bold"))
        quit_button.pack(pady=10)

    def start_game(self):
        """点击开始游戏后关闭主菜单，打开游戏窗口"""
        self.destroy()  # 关闭主菜单窗口
        from presenter.polygon_presenter import PolyPresenter  # 延迟导入避免循环依赖
        from view.polygon_view import PolyView

        presenter = PolyPresenter()  # 创建演示者
        view = PolyView(presenter)  # 视图需要传入演示者

        # view.mainloop()  # 启动游戏界面

    def start_multiplayer(self):
        from view.multiplayer_page import MultiplayerPage #为了避免循环导入，只能放在这里
        from presenter.multiplayer_presenter import MultiplayerPresenter
        self.destroy()
        page = MultiplayerPage()
        presenter = MultiplayerPresenter(page)
        page.mainloop()

    def start_aivs_human(self):
        from view.aivs_human_page import AIVsHumanPage # 同上
        self.destroy()
        ai_vs_human_page = AIVsHumanPage()
        ai_vs_human_page.mainloop()

    def quit_game(self):
        """退出游戏"""
        self.quit()  # 退出应用程序
