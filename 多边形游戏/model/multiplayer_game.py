import socket
import threading
import json
from model.polygon_model import PolyModel  # 导入PolyModel类

class MultiplayerGame(PolyModel):
    def __init__(self, on_message=None):
        super().__init__()  # 调用 PolyModel 的构造函数，初始化 vertices 和 operators
        """
        on_message: 回调函数，接收到服务器消息时调用，签名 on_message(msg: dict) -> None
        """

        self.on_message = on_message
        self.sock = None

    def connect_to_server(self, host: str, port: int):
        """连接到服务器，启动后台接收线程"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        """后台接收服务器消息并分发到回调"""
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("[MultiplayerGame] 连接已关闭")
                    break
                msg = json.loads(data.decode())
                print("[MultiplayerGame] 收到消息:", msg)
                if self.on_message:
                    self.on_message(msg)
            except Exception as e:
                print("[MultiplayerGame] 接收异常:", e)
                break

    def send_data(self, msg: dict):
        """发送 JSON 消息到服务器"""
        try:
            self.sock.send(json.dumps(msg).encode())
        except Exception as e:
            print("[MultiplayerGame] 发送异常:", e)

    # ------ 房间与游戏控制接口 ------

    def create_room(self, room_id: str, player_id: str):
        self.send_data({'type': 'create', 'room_id': room_id, 'player_id': player_id})

    def join_room(self, room_id: str, player_id: str):
        self.send_data({'type': 'join',   'room_id': room_id, 'player_id': player_id})

    def start_game(self, room_id: str, player_id: str):
        self.send_data({'type': 'game_start', 'room_id': room_id, 'player_id': player_id})

    def send_result(self, room_id: str, player_id: str, elapsed: float):
        self.send_data({
            'type': 'result',
            'room_id': room_id,
            'player_id': player_id,
            'elapsed': elapsed
        })
