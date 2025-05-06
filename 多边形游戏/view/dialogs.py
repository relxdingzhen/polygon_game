import tkinter as tk
from tkinter import messagebox


class HistoryDialog(tk.Toplevel):
    def __init__(self, parent, presenter, mode='all'):
        super().__init__(parent)
        self.presenter = presenter  # 保留Presenter引用
        self.title("操作历史记录")
        self.geometry("500x400")

        # 控制面板
        self.mode_var = tk.StringVar(value=mode)
        control_frame = tk.Frame(self)
        tk.Button(control_frame, text="刷新", command=self.refresh).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="全部", variable=self.mode_var, value='all',
                       command=self.refresh).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="最近两步", variable=self.mode_var, value='two',
                       command=self.refresh).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="最近一步", variable=self.mode_var, value='one',
                       command=self.refresh).pack(side=tk.LEFT)
        control_frame.pack(fill=tk.X)

        # 显示区域
        self.text_area = tk.Text(self, wrap=tk.WORD)
        scroll = tk.Scrollbar(self, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scroll.set)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        self.refresh()  # 初始加载数据

    def refresh(self):
        """从模型实时获取最新历史数据"""
        self.update_display(self.mode_var.get())

    def format_step(self, step, step_num):
        """格式化显示合并信息"""
        content = f"步骤 {step_num}:\n"
        content += f"顶点数: {len(step['vertices'])}\n"

        # 显示合并详细信息
        if 'merge_info' in step and step['merge_info']:
            info = step['merge_info']
            content += "┌───────── 合并详情 ────────┐\n"
            content += f"│ 合并顶点: {info['indices'][0] + 1}号({info['values'][0]}) "
            content += f"和 {info['indices'][1] + 1}号({info['values'][1]})\n"
            content += f"│ 运算符: {info['operator']}\n"
            content += f"│ 结果值: {info['result']}\n"
            content += "└──────────────────────┘\n"
        else:
            content += "状态类型: 初始配置\n"

        content += f"当前顶点: {', '.join(map(str, step['vertices']))}\n"
        if len(step['operators']) > 0:
            content += f"剩余运算符: {' → '.join(step['operators'])}\n"
        content += "━" * 40 + "\n"
        return content

    def update_display(self, mode='all'):
        """实时获取最新数据并更新显示"""
        self.text_area.delete(1.0, tk.END)

        # 直接从模型获取最新历史
        history = self.presenter.model.history
        if not history:
            return

        # 应用显示模式过滤
        if mode == 'one':
            display_history = history[-1:]
        elif mode == 'two':
            display_history = history[-2:] if len(history) >= 2 else history
        else:
            display_history = history

        # 生成正确步骤编号
        start_num = max(1, len(history) - len(display_history) + 1)
        for idx, step in enumerate(display_history, start=start_num):
            content = self.format_step(step, idx)
            self.text_area.insert(tk.END, content)

        self.text_area.see(tk.END)  # 滚动到底部


class RangeInputDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("随机生成范围设置")
        self.callback = callback

        tk.Label(self, text="最小值:").grid(row=0, column=0, padx=5, pady=5)
        self.min_entry = tk.Entry(self, width=8)
        self.min_entry.grid(row=0, column=1, padx=5)
        self.min_entry.insert(0, "-10")

        tk.Label(self, text="最大值:").grid(row=1, column=0, padx=5, pady=5)
        self.max_entry = tk.Entry(self, width=8)
        self.max_entry.grid(row=1, column=1, padx=5)
        self.max_entry.insert(0, "10")

        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text="确定", command=self.validate,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=self.destroy,
                  bg="#f44336", fg="white").pack(side=tk.RIGHT, padx=10)
        btn_frame.grid(row=2, columnspan=2, pady=10)

    def validate(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            if min_val > max_val:
                raise ValueError("最小值不能大于最大值")
            self.callback(min_val, max_val)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效的范围设置:\n{str(e)}")


class ManualInputDialog(tk.Toplevel):
    def __init__(self, parent, n, callback):
        super().__init__(parent)
        self.title(f"手动输入 - {n}边形")
        self.callback = callback
        self.entries = []

        # 创建滚动区域
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 添加输入组件
        tk.Label(scrollable_frame, text="顶点值（整数）", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(scrollable_frame, text="运算符（+/×）", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)

        for i in range(n):
            # 顶点输入
            vertex_entry = tk.Entry(scrollable_frame, width=8)
            vertex_entry.grid(row=i + 1, column=0, padx=5, pady=2)

            # 运算符输入
            op_var = tk.StringVar(value='+')
            op_menu = tk.OptionMenu(scrollable_frame, op_var, '+', '×')
            op_menu.config(width=3)
            op_menu.grid(row=i + 1, column=1, padx=5)

            # 标签说明
            tk.Label(scrollable_frame, text=f"顶点 {i + 1} 与 {i + 2 if i + 2 <= n else 1} 之间的符号").grid(row=i + 1,
                                                                                                             column=2,
                                                                                                             sticky='w')

            self.entries.append((vertex_entry, op_var))

        # 确认按钮
        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text="提交", command=self.validate_input,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=self.destroy,
                  bg="#f44336", fg="white").pack(side=tk.RIGHT, padx=10)

        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        btn_frame.pack(pady=10)

    def validate_input(self):
        vertices = []
        operators = []
        errors = []

        for idx, (ventry, opvar) in enumerate(self.entries):
            # 验证顶点值
            try:
                val = int(ventry.get())
                vertices.append(val)
            except ValueError:
                errors.append(f"顶点 {idx + 1} 需要整数")
                ventry.config(highlightbackground='red', highlightthickness=1)

            # 验证运算符
            op = opvar.get().replace('×', '*')  # 转换符号
            operators.append(op)

        if errors:
            messagebox.showerror("输入错误", "\n".join(errors))
            return

        self.callback(vertices, operators)
        self.destroy()
