import math
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk  # 引入ttk模块用于美化

# 自定义样式类
class CustomStyle(ttk.Style):
    def __init__(self):
        super().__init__()
        self.configure('TButton', background='#e3f2fd', foreground='#1565c0', borderwidth=2, relief='solid', bordercolor='#90caf9')
        self.map('TButton',
                 background=[('active', '#bbdefb'), ('hover', '#bbdefb')],
                 foreground=[('active', '#ffffff'), ('hover', '#ffffff')],
                 bordercolor=[('active', '#64b5f6'), ('hover', '#64b5f6')])

class PolygonBoard(tk.Canvas):
    def __init__(self, master, click_callback=None, **kw):
        super().__init__(master, width=400, height=300, bg="#fff9c4", **kw)
        self.click_callback = click_callback
        self.vertices = []
        self.operators = []
        self.bind("<Button-1>", self._click)

    # -------- 绘制多边形 --------
    def draw(self, vertices, operators):
        self.delete("all")
        self.vertices = vertices
        self.operators = operators
        n = len(vertices)

        if n == 1:               # 只剩一个点
            x, y = 200, 150
            self.create_oval(x-25, y-25, x+25, y+25, fill="#E3F2FD")
            self.create_text(x, y, text=str(vertices[0]), font=("Arial",16,"bold"))
            return

        # 均匀分布圆周
        cx, cy, R = 200, 150, 100 if n>3 else 70
        points = []
        for i in range(n):
            ang = 2*math.pi*i/n
            points.append((cx+R*math.cos(ang), cy+R*math.sin(ang)))

        # 画边 + 运算符
        for i,(x1,y1) in enumerate(points):
            x2,y2 = points[(i+1)%n]
            self.create_line(x1,y1,x2,y2, width=2, tags=f"edge_{i}")
            mx,my = (x1+x2)/2, (y1+y2)/2
            self.create_text(mx,my, text=operators[i], font=("Arial",14,"bold"))

        # 画顶点
        for i,(x,y) in enumerate(points):
            self.create_oval(x-15,y-15,x+15,y+15, fill="#FFF9C4")
            self.create_text(x,y, text=str(vertices[i]), font=("Arial",12,"bold"))

    # -------- 点击检测 --------
    def _click(self, ev):
        if not self.click_callback or not self.operators:
            return
        nearest, mind = None, float('inf')
        for i in range(len(self.operators)):
            x1,y1,x2,y2 = self.coords(f"edge_{i}")
            d = PolygonBoard._pt_line_dist(ev.x,ev.y,x1,y1,x2,y2)
            if d < mind:
                mind, nearest = d, i
        if nearest is not None and mind < 10:
            self.click_callback(nearest)

    @staticmethod
    def _pt_line_dist(x,y,x1,y1,x2,y2):
        # 点到线段距离
        if (x1,y1)==(x2,y2):
            return math.hypot(x-x1, y-y1)
        t = ((x-x1)*(x2-x1)+(y-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)
        t = max(0,min(1,t))
        nx,ny = x1+t*(x2-x1), y1+t*(y2-y1)
        return math.hypot(x-nx, y-ny)

# -----------------------------------------------------------------
class AIVsHumanView(tk.Toplevel):
    def __init__(self, presenter, root_page = None):
        super().__init__()
        self.presenter = presenter
        self.root_page = root_page
        self.title("AI 人机对抗")
        self.configure(background='#e3f2fd')  # 设置主背景色
        style = CustomStyle()

        # ---- 顶部信息 ----
        top = tk.Frame(self); top.pack(pady=6)
        self.player_lbl = tk.Label(top, text="玩家得分: ?", font=("Arial",12), background='#e3f2fd', foreground='#1565c0')
        self.ai_lbl = tk.Label(top, text="AI得分: ?", font=("Arial",12), background='#e3f2fd', foreground='#1565c0')
        self.turn_lbl = tk.Label(top, text="玩家回合", font=("Arial",12,"bold"), background='#e3f2fd', foreground='#1565c0')
        self.player_lbl.pack(side=tk.LEFT, padx=20)
        self.ai_lbl.pack(side=tk.LEFT, padx=20)
        self.turn_lbl.pack(side=tk.LEFT, padx=20)

        # # ---- 俩画板 ----
        boards = tk.Frame(self, background='#e3f2fd')
        boards.pack(fill=tk.BOTH, expand=True)

        # 创建一个框架来容纳玩家和AI的画布，确保它们高度一致
        canvas_frame = tk.Frame(boards, background='#e3f2fd')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 玩家画布区域
        player_frame = tk.Frame(canvas_frame, background='#e3f2fd')
        player_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        tk.Label(player_frame, text="玩家", background='#e3f2fd', foreground='#1565c0').pack()
        self.player_board = PolygonBoard(player_frame, click_callback=presenter.on_player_click)
        self.player_board.pack(fill=tk.BOTH, expand=True)

        # AI画布区域
        ai_frame = tk.Frame(canvas_frame, background='#e3f2fd')
        ai_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        tk.Label(ai_frame, text="AI", background='#e3f2fd', foreground='#1565c0').pack()
        self.ai_board = PolygonBoard(ai_frame, click_callback=None)
        self.ai_board.pack(fill=tk.BOTH, expand=True)
        # ---- 底部按钮 ----
        # ---- 底部区域 ----
        bottom = tk.Frame(self, background='#e3f2fd')
        bottom.pack(pady=10)

        # --- 难度选择 ---
        # difficulty_frame = tk.Frame(bottom)
        # tk.Label(difficulty_frame, text="AI难度:").pack(side=tk.LEFT)
        # self.difficulty_var = tk.StringVar(value="easy")
        # tk.OptionMenu(difficulty_frame, self.difficulty_var, "easy", "hard").pack(side=tk.LEFT, padx=6)
        # difficulty_frame.pack(pady=4)

        # --- 控制按钮 ---
        button_frame = tk.Frame(bottom, background='#e3f2fd')
        self.new_btn = ttk.Button(button_frame, text="重玩", width=8, command=self.presenter.new_game,
                                  state=tk.DISABLED)
        exit_btn = ttk.Button(button_frame, text="退出", width=6, command=self._back)
        self.new_btn.pack(side=tk.LEFT, padx=8)
        exit_btn.pack(side=tk.LEFT, padx=8)
        button_frame.pack(pady=4)

        # --- Toast 信息 ---
        self.toast = tk.Label(bottom, text="", fg="blue", background='#e3f2fd')
        self.toast.pack(pady=6)

        print("新建按钮状态：", self.new_btn)

    # -------- 接口供 presenter 调用，也是提供两个画布--------
    def draw_player(self, v, op): self.player_board.draw(v, op)
    def draw_ai(self, v, op): self.ai_board.draw(v, op)

    def update_scores(self, player, ai):
        self.player_lbl.config(text=f"玩家得分: {player}")
        self.ai_lbl.config(text=f"AI得分: {ai}")

    def set_turn(self, txt): self.turn_lbl.config(text=txt)
    def show_toast(self, msg): self.toast.config(text=msg)

    def enable_post_game(self):
        self.new_btn.config(state=tk.NORMAL)
        # self.solve_btn.config(state=tk.NORMAL)

    def _back(self):
        self.destroy()
        if self.root_page:
            self.root_page.deiconify()