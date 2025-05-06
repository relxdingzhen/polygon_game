from view.polygon_view import PolyView
from model.polygon_model import PolyModel
import tkinter as tk
from tkinter import simpledialog, messagebox
from view.dialogs import HistoryDialog, RangeInputDialog, ManualInputDialog

class PolyPresenter:
    def __init__(self):
        self.model = PolyModel()
        self.view = PolyView(self) # 通过构造函数传入视图实例

    def new_game(self):
        n = simpledialog.askinteger("新游戏", "请输入顶点数量：", minvalue=3, maxvalue=10, parent=self.view)
        if not n:
            return

        choice = messagebox.askyesno("输入方式", "是否手动输入具体数值？", parent=self.view)
        if choice is None:
            return

        if choice:
            self.view.wait_window(ManualInputDialog(self.view, n, lambda v, o: self._start_game(n, v, o)))
        else:
            self.view.wait_window(RangeInputDialog(self.view, lambda min_val, max_val: self._start_game(n, min_val=min_val, max_val=max_val)))

    def _start_game(self, n, vertices=None, operators=None, min_val=-10, max_val=10):
        try:
            self.model.initialize(n, vertices=vertices, operators=operators, min_val=min_val, max_val=max_val)
            self.view.draw_polygon(self.model.vertices, self.model.operators)
            self.view.show_toast(f"游戏开始！{n}边形（范围:{min_val}-{max_val}）")
        except Exception as e:
            messagebox.showerror("初始化错误", str(e))

    def on_edge_selected(self, edge_index):
        if len(self.model.vertices) == 1:
            final_score = self.model.vertices[0]
            messagebox.showinfo("游戏结束", f"最终得分: {final_score}\n理论最大值: {self.model.get_max_score()}")
            return

        success = self.model.merge_vertices(edge_index)
        if success:
            self.view.draw_polygon(self.model.vertices, self.model.operators)
            self.view.show_toast(f"合并边 {edge_index} 成功")
        else:
            self.view.show_toast("合并操作失败")

    def undo(self):
        if self.model.undo():
            self.view.draw_polygon(self.model.vertices, self.model.operators)
            self.view.show_toast("撤销成功")
        else:
            self.view.show_toast("无法撤销")

    def redo(self):
        if self.model.redo_stack:
            if self.model.redo():
                self.view.draw_polygon(self.model.vertices, self.model.operators)
                self.view.show_toast("重做成功")
            else:
                self.view.show_toast("重做失败")
        else:
            self.view.show_toast("没有可重做的操作")

    def show_solution(self):
        try:
            max_score, steps = self.model.get_max_score_with_steps()
            detail_window = tk.Toplevel(self.view)
            detail_window.title("动态规划计算过程")
            text_area = tk.Text(detail_window, wrap=tk.WORD, width=80, height=30)
            scroll = tk.Scrollbar(detail_window, command=text_area.yview)
            text_area.configure(yscrollcommand=scroll.set)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_area.insert(tk.END, "===== 动态规划计算步骤 =====\n\n")
            for step in steps:
                text_area.insert(tk.END, step + "\n")
            text_area.configure(state='disabled')
            messagebox.showinfo("最优解", f"理论最大值: {max_score}\n当前顶点数: {len(self.model.vertices)}")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败: {str(e)}")

    def show_history(self, mode='all'):
        from view.dialogs import HistoryDialog
        HistoryDialog(self.view, self, mode)


