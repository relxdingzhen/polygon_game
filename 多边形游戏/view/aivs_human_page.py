import tkinter as tk
from presenter.aivs_human_presenter import AIVsHumanPresenter
from view.main_page import MainPage   # 你的主菜单页面

class AIVsHumanPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI 人机对抗")
        self.geometry("400x250")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="AI 人机对抗", font=("Arial", 16, "bold")).pack(pady=25)
        tk.Button(self, text="开始对抗", width=18, height=2,
                  bg="#FF9800", fg="white",
                  command=self._start).pack(pady=20)
        tk.Button(self, text="返回主菜单", width=18, height=2,
                  bg="#9C27B0", fg="white",
                  command=self._back).pack()

    def _start(self):
        self.withdraw()                 # 隐藏当前菜单窗
        AIVsHumanPresenter(self)        # 顶层交由 presenter

    def _back(self):
        self.destroy()
        MainPage().mainloop()
