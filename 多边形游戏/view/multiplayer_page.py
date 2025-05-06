import tkinter as tk
from tkinter import simpledialog, messagebox
from view.main_page import MainPage

class MultiplayerPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("多人对战")
        self.geometry("400x300")
        self.presenter = None
        self.setup()

    def setup(self):
        tk.Button(self, text="创建房间", command=self._create).pack(pady=5)
        tk.Button(self, text="加入房间", command=self._join).pack(pady=5)
        self.start_btn = tk.Button(self, text="开始游戏", state=tk.DISABLED, command=self._start)
        self.start_btn.pack(pady=5)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(self, text="返回", command=self._back).pack(pady=5)

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
