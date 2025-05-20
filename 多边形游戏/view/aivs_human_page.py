import tkinter as tk
from presenter.aivs_human_presenter import AIVsHumanPresenter
from view.main_page import MainPage   # 你的主菜单页面

class AIVsHumanPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI 人机对抗")
        self.geometry("400x250")
        self.resizable(False, False)
        self.configure(background="#e3f2fd")
        self._build_ui()

    def _build_ui(self):
        title_label = tk.Label(self, text="AI 人机对抗", font=("Arial", 16, "bold"),bg="#e3f2fd")
        title_label.pack(pady=25)

        button_style = {
            "width": 18,
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

        start_button = tk.Button(self, text="开始对抗", width=18, height=2,
                                 bg="#e3f2fd", fg="#1565c0",
                                 command=self._start)           # FF9800
        start_button.pack(pady=20)
        start_button.bind("<Enter>", lambda event, btn=start_button: self.on_enter(btn))
        start_button.bind("<Leave>", lambda event, btn=start_button: self.on_leave(btn))

        back_button = tk.Button(self, text="返回主菜单", width=18, height=2,
                                bg="#e3f2fd", fg="#1565c0",
                                command=self._back)             # 9C27B0
        back_button.pack()
        back_button.bind("<Enter>", lambda event, btn=back_button: self.on_enter(btn))
        back_button.bind("<Leave>", lambda event, btn=back_button: self.on_leave(btn))

    def on_enter(self, button):
        button.config(bg="#bbdefb", fg="#ffffff", highlightbackground="#64b5f6", highlightcolor="#64b5f6")

    def on_leave(self, button):
        button.config(bg="#e3f2fd", fg="#1565c0", highlightbackground="#90caf9", highlightcolor="#90caf9")

    def _start(self):
        self.withdraw()                 # 隐藏当前菜单窗
        AIVsHumanPresenter(self)        # 顶层交由 presenter

    def _back(self):
        self.destroy()
        MainPage().mainloop()
