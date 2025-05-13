import tkinter as tk
from tkinter import simpledialog, messagebox
from view.main_page import MainPage

class MultiplayerPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("多人对战")
        self.geometry("400x300")
        self.presenter = None
        self.configure(background="#e3f2fd")
        self.setup()

    def setup(self):
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
        create_button = tk.Button(self, text="创建房间", command=self._create, **button_style)
        create_button.pack(pady=5)
        create_button.bind("<Enter>", lambda event, btn=create_button: self.on_enter(btn))
        create_button.bind("<Leave>", lambda event, btn=create_button: self.on_leave(btn))

        join_button = tk.Button(self, text="加入房间", command=self._join, **button_style)
        join_button.pack(pady=5)
        join_button.bind("<Enter>", lambda event, btn=join_button: self.on_enter(btn))
        join_button.bind("<Leave>", lambda event, btn=join_button: self.on_leave(btn))

        self.start_btn = tk.Button(self, text="开始游戏", state=tk.DISABLED, command=self._start, **button_style)
        self.start_btn.pack(pady=5)
        self.start_btn.bind("<Enter>", lambda event, btn=self.start_btn: self.on_enter(btn))
        self.start_btn.bind("<Leave>", lambda event, btn=self.start_btn: self.on_leave(btn))

        self.listbox = tk.Listbox(self, bg="#fff9c4", bd=4, relief=tk.SOLID, highlightbackground="#ffd54f", highlightcolor="#ffd54f", highlightthickness=4, borderwidth=0)
        self.listbox.pack(fill=tk.X, padx=20, pady=10)

        back_button = tk.Button(self, text="返回", command=self._back)
        back_button.pack(pady=5)
        back_button.bind("<Enter>", lambda event, btn=back_button: self.on_enter(btn))
        back_button.bind("<Leave>", lambda event, btn=back_button: self.on_leave(btn))

    def on_enter(self, button):
        button.config(bg="#bbdefb", fg="#ffffff", highlightbackground="#64b5f6", highlightcolor="#64b5f6")

    def on_leave(self, button):
        button.config(bg="#e3f2fd", fg="#1565c0", highlightbackground="#90caf9", highlightcolor="#90caf9")


    def _create(self):
        room_id = simpledialog.askstring("创建房间", "输入房间ID:")
        if room_id and self.presenter:
            self.presenter.create_room(room_id)

    def _join(self):
        room_id = simpledialog.askstring("加入房间", "输入房间ID:")
        if room_id and self.presenter:
            self.presenter.join_room(room_id)

    def _start(self):
        if self.presenter:
            self.presenter.start_game()

    def update_player_list(self, players):
        self.listbox.delete(0, tk.END)
        for p in players:
            self.listbox.insert(tk.END, p)

    def enable_start(self, ok: bool):
        self.start_btn.config(state=tk.NORMAL if ok else tk.DISABLED)

    def _back(self):
        self.destroy()
        MainPage().mainloop()
