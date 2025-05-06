import tkinter as tk
from view.main_page import MainPage  # 导入主菜单页面

class AIVsHumanPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI人机对抗")
        self.geometry("400x300")
        self.resizable(False, False)
        self.setup_ui()

    def setup_ui(self):
        # 设置标题
        title_label = tk.Label(self, text="AI人机对抗", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # 开始游戏按钮
        start_button = tk.Button(self, text="开始对抗", width=20, height=2, command=self.start_ai_vs_human_game, bg="#FF9800", fg="white", font=("Arial", 12, "bold"))
        start_button.pack(pady=20)

        # 返回主菜单按钮
        back_button = tk.Button(self, text="返回主菜单", width=20, height=2, command=self.back_to_main_menu, bg="#9C27B0", fg="white", font=("Arial", 12, "bold"))
        back_button.pack(pady=10)

    def start_ai_vs_human_game(self):
        # 游戏逻辑
        print("开始AI人机对抗游戏")
        # 你可以在这里实现游戏的逻辑，但不需要再次创建返回按钮

    def back_to_main_menu(self):
        """返回主菜单"""
        self.destroy()  # 销毁当前页面
        main_page = MainPage()  # 创建主菜单页面
        main_page.mainloop()  # 启动主菜单页面
