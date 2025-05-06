# presenter/multiplayer_presenter.py

import time
import random
import tkinter.messagebox as mb
from model.multiplayer_game import MultiplayerGame
from view.polygon_view import PolyView

class MultiplayerPresenter:
    def __init__(self, view, host='127.0.0.1', port=9999):
        self.view = view
        self.view.presenter = self
        self.room_id   = None
        self.player_id = f"P_{random.randint(1000, 9999)}"
        self.is_host   = False
        self.start_ts  = None

        self.model = MultiplayerGame(on_message=self.on_network_message)
        self.model.connect_to_server(host, port)

    def on_network_message(self, msg: dict):
        t = msg.get('type')
        print("[Presenter] on_network_message 收到", msg)
        if t == 'player_joined':
            players = msg['players']
            self.view.update_player_list(players)
            self.view.enable_start(len(players) == 2)

        elif t == 'game_start':
            verts, ops = msg['vertices'], msg['operators']
            self.start_ts = time.time()
            # 把创建视图的逻辑调度到主线程，并直接写在 lambda 里
            def open_view():
                self.view.withdraw()
                self.game_view = PolyView(self)
                self.game_view.draw_polygon(verts, ops)
            self.view.after(0, open_view)

        elif t == 'game_result':
            winner = msg['winner']; times = msg['times']
            your = times.get(self.player_id, 0)
            opp  = next(v for k, v in times.items() if k != self.player_id)
            if winner == self.player_id:
                mb.showinfo("比赛结果",
                    f"你赢了！\n你的时间: {your:.2f}s\n对手: {opp:.2f}s")
            else:
                mb.showinfo("比赛结果",
                    f"你输了…\n你的时间: {your:.2f}s\n赢家: {winner}")
            self.view.after(0, self.view.deiconify)

    def new_game(self):
        self.start_game()

    def undo(self):
        mb.showinfo("提示", "多人模式不支持撤销")

    def redo(self):
        mb.showinfo("提示", "多人模式不支持重做")

    def show_solution(self):
        mb.showinfo("提示", "多人模式不支持查看最优解")

    def show_history(self):
        mb.showinfo("提示", "多人模式不支持历史记录")

    def create_room(self, room_id: str):
        self.is_host = True
        self.room_id = room_id
        print(f"[Presenter] 创建房间 {room_id}")
        self.model.create_room(room_id, self.player_id)

    def join_room(self, room_id: str):
        self.room_id = room_id
        print(f"[Presenter] 加入房间 {room_id}")
        self.model.join_room(room_id, self.player_id)

    def start_game(self):
        if not self.is_host:
            mb.showinfo("提示", "只有房主可以开始游戏")
            return
        print(f"[Presenter] 发起 game_start in {self.room_id}")
        self.model.start_game(self.room_id, self.player_id)

    def finish(self):
        if self.start_ts is None:
            return
        elapsed = time.time() - self.start_ts
        print(f"[Presenter] 上报耗时 {elapsed:.2f}s")
        self.model.send_result(self.room_id, self.player_id, elapsed)

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