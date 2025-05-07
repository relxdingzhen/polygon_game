# presenter/multiplayer_presenter.py

import time
import random
import tkinter.messagebox as mb
from tkinter import simpledialog
from model.multiplayer_game import MultiplayerGame
from view.polygon_view import PolyView
import json

class MultiplayerPresenter:
    def __init__(self, view, host='127.0.0.1', port=9999):
        self.view = view
        self.view.presenter = self
        self.room_id   = None
        self.player_id = f"P_{random.randint(1000, 9999)}"
        self.is_host   = False
        self.start_ts  = None
        self.countdown = None
        self.game_started = False
        self.game_config = {'n': 4, 'min_val': 1, 'max_val': 100}
        self.hosts = {}  # room_id -> player_id

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
            # 保存游戏配置
            self.game_config = {
                'n': msg.get('n', 4),
                'min_val': msg.get('min_val', 1),
                'max_val': msg.get('max_val', 100)
            }
            # 初始化模型数据
            self.model.initialize_game(verts, ops)
            # 开始倒计时
            self.start_countdown()
            # 把创建视图的逻辑调度到主线程，并直接写在 lambda 里
            def open_view():
                self.view.withdraw()
                self.game_view = PolyView(self)
                self.game_view.draw_polygon(verts, ops)
                # 显示游戏配置信息
                self.game_view.show_toast(
                    f"游戏配置：{self.game_config['n']}边形 "
                    f"（范围:{self.game_config['min_val']}-{self.game_config['max_val']}）"
                )
            self.view.after(0, open_view)

        elif t == 'game_result':
            results = msg['results']
            winner = msg['winner']
            your_result = results[self.player_id]
            opp_id = next(k for k in results.keys() if k != self.player_id)
            opp_result = results[opp_id]
            
            # 构建结果消息
            result_msg = "=" * 30 + "\n"
            result_msg += "比赛结果\n"
            result_msg += "=" * 30 + "\n\n"
            
            # 显示双方成绩
            result_msg += f"你的成绩：\n"
            result_msg += f"分数: {your_result['score']}\n"
            result_msg += f"用时: {your_result['elapsed']:.2f}秒\n\n"
            
            result_msg += f"对手成绩：\n"
            result_msg += f"分数: {opp_result['score']}\n"
            result_msg += f"用时: {opp_result['elapsed']:.2f}秒\n\n"
            
            # 显示胜负结果
            result_msg += "=" * 30 + "\n"
            if winner == self.player_id:
                result_msg += "🎉 恭喜你获胜！ 🎉\n"
            else:
                result_msg += f"🏆 {opp_id} 获胜！ 🏆\n"
            result_msg += "=" * 30
            
            # 直接使用 messagebox 显示结果
            mb.showinfo("比赛结果", result_msg)
            self.view.deiconify()

        elif t == 'room_update':
            players = msg['players']
            host = msg['host']
            self.view.update_player_list(players)
            old_is_host = self.is_host
            self.is_host = (self.player_id == host)
            # 只有当玩家从非房主变成房主时才显示提示
            if not old_is_host and self.is_host and msg.get('host_changed', False):
                mb.showinfo("房主变更", "你现在是新的房主，可以开始游戏。")
            # 只有两人才能开始游戏
            self.view.enable_start(len(players) == 2 and self.is_host)

        elif t == 'error':
            mb.showerror("错误", msg.get('msg', '未知错误'))

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
            
        # 房主可以配置游戏参数
        n = simpledialog.askinteger("游戏配置", "请输入顶点数量：", 
                                  minvalue=3, maxvalue=10, 
                                  initialvalue=self.game_config['n'])
        if not n:
            return
            
        min_val = simpledialog.askinteger("游戏配置", "请输入最小值：",
                                        initialvalue=self.game_config['min_val'])
        if min_val is None:
            return
            
        max_val = simpledialog.askinteger("游戏配置", "请输入最大值：",
                                        minvalue=min_val+1,
                                        initialvalue=self.game_config['max_val'])
        if max_val is None:
            return
            
        self.game_config = {'n': n, 'min_val': min_val, 'max_val': max_val}
        print(f"[Presenter] 发起 game_start in {self.room_id} with config: {self.game_config}")
        self.model.start_game(self.room_id, self.player_id, **self.game_config)

    def start_countdown(self):
        """开始3秒倒计时"""
        self.countdown = 3
        self.game_started = False
        self.update_countdown()

    def update_countdown(self):
        """更新倒计时显示"""
        if self.countdown > 0:
            if hasattr(self, 'game_view'):
                self.game_view.show_toast(f"游戏将在 {self.countdown} 秒后开始...")
            self.countdown -= 1
            self.view.after(1000, self.update_countdown)
        else:
            self.game_started = True
            if hasattr(self, 'game_view'):
                self.game_view.show_toast("游戏开始！")

    def finish(self):
        if self.start_ts is None:
            return
        elapsed = time.time() - self.start_ts
        final_score = self.model.vertices[0] if len(self.model.vertices) == 1 else 0
        print(f"[Presenter] 上报结果 分数:{final_score} 耗时:{elapsed:.2f}s")
        self.model.send_result(self.room_id, self.player_id, final_score, elapsed)

    def on_edge_selected(self, edge_index):
        if not self.game_started:
            self.game_view.show_toast("游戏还未开始，请等待倒计时结束")
            return
            
        if len(self.model.vertices) == 1:
            # 游戏结束，发送结果到服务器
            final_score = self.model.vertices[0]
            elapsed = time.time() - self.start_ts
            print(f"[Presenter] 游戏结束，发送结果：分数={final_score}，用时={elapsed:.2f}秒")
            
            # 直接使用 messagebox 显示结果
            mb.showinfo("游戏结束", 
                f"你已完成游戏！\n"
                f"最终得分: {final_score}\n"
                f"用时: {elapsed:.2f}秒\n\n"
                f"等待对手完成游戏..."
            )
            # 发送结果到服务器
            self.model.send_result(self.room_id, self.player_id, final_score, elapsed)
            return

        success = self.model.merge_vertices(edge_index)
        if success:
            self.game_view.draw_polygon(self.model.vertices, self.model.operators)
            self.game_view.show_toast(f"合并边 {edge_index} 成功")
            # 新增：合并后立即检测是否只剩一个节点
            if len(self.model.vertices) == 1:
                final_score = self.model.vertices[0]
                elapsed = time.time() - self.start_ts
                mb.showinfo("游戏结束", 
                    f"你已完成游戏！\n"
                    f"最终得分: {final_score}\n"
                    f"用时: {elapsed:.2f}秒\n\n"
                    f"等待对手完成游戏..."
                )
                self.model.send_result(self.room_id, self.player_id, final_score, elapsed)
                return
        else:
            self.game_view.show_toast("合并操作失败")