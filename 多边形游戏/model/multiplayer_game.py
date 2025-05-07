import socket
import threading
import json
from model.polygon_model import PolyModel  # 导入PolyModel类
import copy
import time

class MultiplayerGame(PolyModel):
    def __init__(self, on_message=None):
        super().__init__()  # 调用 PolyModel 的构造函数，初始化 vertices 和 operators
        """
        on_message: 回调函数，接收到服务器消息时调用，签名 on_message(msg: dict) -> None
        """
        self.on_message = on_message
        self.sock = None
        self.host = None
        self.port = None
        self.connected = False
        self.reconnect_thread = None

    def initialize_game(self, vertices, operators):
        """初始化游戏数据"""
        self.vertices = vertices
        self.operators = operators
        # 初始化历史记录
        self.history = [{
            "vertices": copy.deepcopy(self.vertices),
            "operators": copy.deepcopy(self.operators)
        }]
        self.current_step = 0
        self.redo_stack = []

    def connect_to_server(self, host: str, port: int):
        """连接到服务器，启动后台接收线程"""
        self.host = host
        self.port = port
        self._try_connect()

    def _try_connect(self):
        """尝试连接到服务器"""
        try:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            if self.reconnect_thread is None:
                threading.Thread(target=self._recv_loop, daemon=True).start()
        except Exception as e:
            print(f"[MultiplayerGame] 连接失败: {e}")
            self.connected = False
            if self.on_message:
                self.on_message({'type': 'error', 'msg': f'连接服务器失败: {str(e)}'})

    def _recv_loop(self):
        """后台接收服务器消息并分发到回调"""
        while True:
            try:
                if not self.connected:
                    time.sleep(1)  # 等待重连
                    continue
                    
                data = self.sock.recv(1024)
                if not data:
                    print("[MultiplayerGame] 连接已关闭，尝试重连...")
                    self.connected = False
                    self._try_connect()
                    continue
                    
                msg = json.loads(data.decode())
                print("[MultiplayerGame] 收到消息:", msg)
                if self.on_message:
                    self.on_message(msg)
            except json.JSONDecodeError as e:
                print("[MultiplayerGame] JSON解析错误:", e)
                continue
            except ConnectionError as e:
                print("[MultiplayerGame] 连接错误:", e)
                self.connected = False
                self._try_connect()
                continue
            except Exception as e:
                print("[MultiplayerGame] 接收异常:", e)
                self.connected = False
                self._try_connect()
                continue

    def send_data(self, msg: dict):
        """发送 JSON 消息到服务器"""
        if not self.connected:
            print("[MultiplayerGame] 未连接到服务器，尝试重连...")
            self._try_connect()
            if not self.connected:
                if self.on_message:
                    self.on_message({'type': 'error', 'msg': '未连接到服务器'})
                return
                
        try:
            self.sock.send(json.dumps(msg).encode())
        except Exception as e:
            print("[MultiplayerGame] 发送异常:", e)
            self.connected = False
            self._try_connect()
            if self.on_message:
                self.on_message({'type': 'error', 'msg': f'发送消息失败: {str(e)}'})

    # ------ 房间与游戏控制接口 ------

    def create_room(self, room_id: str, player_id: str):
        self.send_data({'type': 'create', 'room_id': room_id, 'player_id': player_id})

    def join_room(self, room_id: str, player_id: str):
        self.send_data({'type': 'join',   'room_id': room_id, 'player_id': player_id})

    def start_game(self, room_id: str, player_id: str, n=4, min_val=1, max_val=100):
        self.send_data({
            'type': 'game_start',
            'room_id': room_id,
            'player_id': player_id,
            'n': n,
            'min_val': min_val,
            'max_val': max_val
        })

    def send_result(self, room_id: str, player_id: str, score: int, elapsed: float):
        self.send_data({
            'type': 'result',
            'room_id': room_id,
            'player_id': player_id,
            'score': score,
            'elapsed': elapsed
        })

    def get_max_score(self):
        """计算理论最大值"""
        if not self.vertices:
            return 0
        if len(self.vertices) == 1:
            return self.vertices[0]
            
        # 扩展数组处理环形结构
        n = len(self.vertices)
        nums = self.vertices * 2
        ops = self.operators * 2
        dp_max = [[-float('inf')] * (2 * n) for _ in range(2 * n)]
        
        # 初始化对角线
        for i in range(2 * n):
            dp_max[i][i] = nums[i]
            
        # 动态规划计算
        for length in range(1, n):
            for i in range(2 * n - length):
                j = i + length
                for k in range(i, j):
                    op = ops[k]
                    if op == '+':
                        dp_max[i][j] = max(dp_max[i][j], dp_max[i][k] + dp_max[k + 1][j])
                    else:  # '*'
                        dp_max[i][j] = max(dp_max[i][j], dp_max[i][k] * dp_max[k + 1][j])
        
        # 返回所有可能的起点中的最大值
        return max(dp_max[i][i + n - 1] for i in range(n))
