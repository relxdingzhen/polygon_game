# presenter/aivs_human_presenter.py
import random
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import List

from model.aivs_human_game import AIModel
from view.aivs_human_view import AIVsHumanView

class AIVsHumanPresenter:
    def __init__(self, root):
        self.root = root               # 传入顶窗口或上一页面
        self.view = AIVsHumanView(self, root_page=root)
        self.new_game()                # 自动开局

    # ---------- 开新局 ----------
    def new_game(self):
        n = simpledialog.askinteger("配置", "顶点数 n (3-10):",
                                     minvalue=3, maxvalue=10, parent=self.view)
        if not n: return
        min_v = simpledialog.askinteger("范围", "最小值:", initialvalue=-10, parent=self.view)
        max_v = simpledialog.askinteger("范围", "最大值:", initialvalue=10 , parent=self.view)
        if min_v is None or max_v is None or min_v >= max_v:
            messagebox.showerror("输入错误", "范围不合法", parent=self.view)
            return

        # 生成同一份初始图
        vertices = [random.randint(min_v, max_v) for _ in range(n)]
        ops = [random.choice(['+', '*']) for _ in range(n)]

        # 模型 ×2
        self.player = AIModel(); self.player.initialize(n, vertices, ops)
        self.ai = AIModel(); self.ai.initialize    (n, vertices, ops)

        # 初始渲染
        self.view.draw_player(vertices, ops)
        self.view.draw_ai(vertices, ops)
        self.view.update_scores("?", "?")
        self.view.set_turn("玩家回合")
        self.view.show_toast("点击一条边进行合并…")
        self.post_game = False
        self.view.enable_post_game()      # 先禁用，它会在结束时再启
        self.view.new_btn.config(state=tk.DISABLED)
        self.view.solve_btn.config(state=tk.DISABLED)

    # ---------- 玩家点击 ----------
    def on_player_click(self, edge_idx: int):
        if self.post_game or len(self.player.vertices) == 1:
            return
        if not self.player.merge_vertices(edge_idx):
            self.view.show_toast("非法选择")
            return
        self.view.draw_player(self.player.vertices, self.player.operators)
        self.view.set_turn("AI 回合")
        self.view.show_toast("AI 正在思考…")
        self.root.after(1500, self._ai_move) # 让AI假装思考..

    # ---------- AI 回合 ----------
    def _ai_move(self):
        if len(self.ai.vertices) > 1:
            best = self.ai.get_best_edge()
            self.ai.merge_vertices(best)
            self.view.draw_ai(self.ai.vertices, self.ai.operators)

        self._check_end_or_next()

    # ---------- 检查是否结束 ----------
    def _check_end_or_next(self):
        if len(self.player.vertices) > 1 or len(self.ai.vertices) > 1:
            # 继续
            self.view.set_turn("玩家回合")
            self.view.show_toast("轮到你了！")
            return

        # 游戏结束
        p_score = self.player.vertices[0]
        a_score = self.ai.vertices[0]
        self.view.update_scores(p_score, a_score)

        if p_score > a_score:
            msg = f"🎉 玩家胜！({p_score} > {a_score})"
        elif p_score < a_score:
            msg = f"😈 AI 胜！({a_score} > {p_score})"
        else:
            msg = f"🤝 平局！({p_score})"
        messagebox.showinfo("结果", msg, parent=self.view)
        self.view.show_toast(msg)
        self.view.set_turn("游戏结束")
        self.post_game = True
        self.view.enable_post_game()

    # ---------- 查看 AI 全局最优解 ----------
    def show_solution(self):
        score, steps = self.ai.get_max_score_with_steps()
        # self._show_steps_window("AI 全局最优解", score, steps)

    # ---------- 弹窗显示步骤 ----------
    def _show_steps_window(self, title: str, score: int, steps: List[str]):
        win = tk.Toplevel(self.view)
        win.title(title)
        txt = tk.Text(win, wrap=tk.WORD, width=90, height=35)
        sb = tk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt.insert(tk.END, f"{title}\n最终得分: {score}\n\n")
        for s in steps:
            txt.insert(tk.END, s + "\n")
        txt.configure(state=tk.DISABLED)
