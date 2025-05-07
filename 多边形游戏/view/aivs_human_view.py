# view/aivs_human_view.py
import math
import tkinter as tk

class PolygonBoard(tk.Canvas):
    def __init__(self, master, click_callback=None, **kw):
        super().__init__(master, width=400, height=300, bg="white", **kw)
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

        # ---- 顶部信息 ----
        top = tk.Frame(self); top.pack(pady=6)
        self.player_lbl = tk.Label(top, text="玩家得分: ?", font=("Arial",12))
        self.ai_lbl = tk.Label(top, text="AI得分: ?", font=("Arial",12))
        self.turn_lbl = tk.Label(top, text="玩家回合", font=("Arial",12,"bold"))
        self.player_lbl.pack(side=tk.LEFT, padx=20)
        self.ai_lbl.pack(side=tk.LEFT, padx=20)
        self.turn_lbl.pack(side=tk.LEFT, padx=20)

        # ---- 俩画板 ----
        boards = tk.Frame(self); boards.pack()
        self.player_board = PolygonBoard(boards, click_callback=presenter.on_player_click)
        self.ai_board = PolygonBoard(boards, click_callback=None)
        tk.Label(boards, text="玩家").pack()
        self.player_board.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(boards, text="AI").pack()
        self.ai_board.pack(side=tk.LEFT, padx=10, pady=5)

        # ---- 底部按钮 ----
        btns = tk.Frame(self); btns.pack(pady=8)
        self.new_btn   = tk.Button(btns, text="重玩", width=8,
                                   command=presenter.new_game, state=tk.DISABLED)
        # self.solve_btn = tk.Button(btns, text="查看AI最优解", width=14,
        #                            command=presenter.show_solution, state=tk.DISABLED)
        tk.Button(btns, text="退出", width=6, command=self._back).pack(side=tk.LEFT, padx=8)
        self.new_btn.pack(side=tk.LEFT, padx=8)
        # self.solve_btn.pack(side=tk.LEFT, padx=8)

        # ---- Toast ----
        self.toast = tk.Label(self, text="", fg="blue")
        self.toast.pack()

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


