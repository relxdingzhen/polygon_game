import socket, threading, json, random, time
from collections import defaultdict

HOST = '0.0.0.0'
PORT = 9999

class GameServer:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.bind((HOST, PORT))
        self.sock.listen()
        # 房间映射 room_id -> { player_id: conn }
        self.rooms = defaultdict(dict)
        # 结果临时存储 room_id -> { player_id: elapsed }
        self.results = defaultdict(dict)
        print(f"[服务器] 启动于 {HOST}:{PORT}")

    def start(self):
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            conn, _ = self.sock.accept()
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data: break
                msg = json.loads(data.decode())
                t = msg['type']; room = msg.get('room_id'); pid = msg.get('player_id')

                # 创建/加入房间
                if t in ('create','join'):
                    # create: 如果已存在则返回失败（可扩展）；join: 直接加入
                    self.rooms[room][pid] = conn
                    # 通知该房间所有客户端
                    self._broadcast(room, {
                        'type': 'player_joined',
                        'players': list(self.rooms[room].keys())
                    })

                # 游戏开始：只主机可发
                # elif t=='game_start':
                #     if len(self.rooms[room])!=2: continue
                #     n = msg.get('n', 4)  # 默认 4 边
                #     verts = [random.randint(1, 100) for _ in range(n)]
                #     ops = [random.choice(['+', '*']) for _ in range(n)]
                #     payload = {
                #         'type': 'game_start',
                #         'vertices': verts,
                #         'operators': ops,
                #         'start_ts': time.time()
                #     }
                #     self.results[room].clear()
                #     self._broadcast(room, payload)
                elif t == 'game_start':
                    if len(self.rooms[room]) != 2:
                        continue

                    n = msg.get('n', 4)  # 节点个数，默认4
                    min_val = msg.get('min_val', 1)  # 最小值，默认1
                    max_val = msg.get('max_val', 100)  # 最大值，默认100

                    verts = [random.randint(min_val, max_val) for _ in range(n)]
                    ops = [random.choice(['+', '*']) for _ in range(n)]

                    payload = {
                        'type': 'game_start',
                        'vertices': verts,
                        'operators': ops,
                        'start_ts': time.time()
                    }

                    self.results[room].clear()
                    self._broadcast(room, payload)

                # 客户端上报结果
                elif t=='result':
                    elapsed = msg['elapsed']
                    self.results[room][pid] = elapsed
                    if set(self.results[room].keys())==set(self.rooms[room].keys()):
                        # 决出胜负
                        winner = min(self.results[room], key=self.results[room].get)
                        payload = {
                            'type':'game_result',
                            'winner': winner,
                            'times': self.results[room]
                        }
                        self._broadcast(room, payload)

    def _broadcast(self, room, msg):
        for c in list(self.rooms[room].values()):
            try: c.send(json.dumps(msg).encode())
            except: pass

if __name__=='__main__':
    GameServer().start()
    print("[服务器] 运行中… Ctrl+C 退出")
    threading.Event().wait()
