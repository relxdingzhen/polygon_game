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
        # 结果临时存储 room_id -> { player_id: {score: int, elapsed: float} }
        self.results = defaultdict(dict)
        print(f"[服务器] 启动于 {HOST}:{PORT}")

    def start(self):
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            conn, _ = self.sock.accept()
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn):
        room = None
        pid = None
        try:
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data: break
                    msg = json.loads(data.decode())
                    t = msg['type']; room = msg.get('room_id'); pid = msg.get('player_id')

                    # 创建房间
                    if t == 'create':
                        if room in self.rooms and self.rooms[room]:
                            try:
                                conn.send(json.dumps({'type': 'error', 'msg': '房间已存在'}).encode())
                            except: pass
                            return
                        self.rooms[room][pid] = conn
                        if not hasattr(self, 'hosts'):
                            self.hosts = {}
                        self.hosts[room] = pid  # 设置房主
                        self._broadcast(room, {
                            'type': 'player_joined',
                            'players': list(self.rooms[room].keys())
                        })

                    # 加入房间
                    elif t == 'join':
                        if room not in self.rooms or not self.rooms[room]:
                            try:
                                conn.send(json.dumps({'type': 'error', 'msg': '房间不存在，请先创建房间'}).encode())
                            except: pass
                            return
                        self.rooms[room][pid] = conn
                        self._broadcast(room, {
                            'type': 'player_joined',
                            'players': list(self.rooms[room].keys())
                        })

                    # 游戏开始
                    elif t == 'game_start':
                        if len(self.rooms[room]) != 2:
                            continue
                        n = msg.get('n', 4)
                        min_val = msg.get('min_val', 1)
                        max_val = msg.get('max_val', 100)
                        verts = [random.randint(min_val, max_val) for _ in range(n)]
                        ops = [random.choice(['+', '*']) for _ in range(n)]
                        payload = {
                            'type': 'game_start',
                            'vertices': verts,
                            'operators': ops,
                            'start_ts': time.time(),
                            'n': n,
                            'min_val': min_val,
                            'max_val': max_val
                        }
                        self.results[room].clear()
                        self._broadcast(room, payload)

                    # 客户端上报结果
                    elif t=='result':
                        score = msg['score']
                        elapsed = msg['elapsed']
                        print(f"[服务器] 收到玩家 {pid} 的结果：分数={score}，用时={elapsed:.2f}秒")
                        self.results[room][pid] = {'score': score, 'elapsed': elapsed}
                        if set(self.results[room].keys())==set(self.rooms[room].keys()):
                            print(f"[服务器] 所有玩家完成游戏，开始计算结果")
                            players = list(self.results[room].keys())
                            if len(players) == 2:
                                p1, p2 = players
                                r1, r2 = self.results[room][p1], self.results[room][p2]
                                print(f"[服务器] 玩家1 {p1}: 分数={r1['score']}, 用时={r1['elapsed']:.2f}秒")
                                print(f"[服务器] 玩家2 {p2}: 分数={r2['score']}, 用时={r2['elapsed']:.2f}秒")
                                if r1['score'] > r2['score']:
                                    winner = p1
                                    print(f"[服务器] {p1} 获胜（分数更高）")
                                elif r2['score'] > r1['score']:
                                    winner = p2
                                    print(f"[服务器] {p2} 获胜（分数更高）")
                                else:
                                    winner = p1 if r1['elapsed'] < r2['elapsed'] else p2
                                    print(f"[服务器] {winner} 获胜（用时更短）")
                                payload = {
                                    'type': 'game_result',
                                    'winner': winner,
                                    'results': {
                                        p1: {'score': r1['score'], 'elapsed': r1['elapsed']},
                                        p2: {'score': r2['score'], 'elapsed': r2['elapsed']}
                                    }
                                }
                                print(f"[服务器] 广播游戏结果：{payload}")
                                self._broadcast(room, payload)
        finally:
            # 断开连接后清理
            if room and pid:
                if pid in self.rooms[room]:
                    del self.rooms[room][pid]
                # 房主断开，自动转移
                if hasattr(self, 'hosts') and room in self.hosts and self.hosts[room] == pid:
                    if self.rooms[room]:
                        new_host = next(iter(self.rooms[room].keys()))
                        self.hosts[room] = new_host
                    else:
                        del self.hosts[room]
                # 广播最新房间成员和房主
                if self.rooms.get(room):
                    self._broadcast(room, {
                        'type': 'room_update',
                        'players': list(self.rooms[room].keys()),
                        'host': self.hosts.get(room)
                    })
                # 房间没人了，清理
                if not self.rooms[room]:
                    del self.rooms[room]
                    if room in self.results:
                        del self.results[room]
                    if hasattr(self, 'hosts') and room in self.hosts:
                        del self.hosts[room]

    def _broadcast(self, room, msg):
        to_remove = []
        for pid, c in list(self.rooms[room].items()):
            try:
                c.send(json.dumps(msg).encode())
            except:
                to_remove.append(pid)
        # 移除失效连接
        for pid in to_remove:
            del self.rooms[room][pid]
        # 如果房间没人了，清理房间和结果
        if not self.rooms[room]:
            if room in self.results:
                del self.results[room]
            if hasattr(self, 'hosts') and room in self.hosts:
                del self.hosts[room]
            del self.rooms[room]
            print(f"[服务器] 房间 {room} 已释放")
            return
        # 广播最新房间成员和房主
        if msg.get('type') != 'room_update':
            # 获取当前房主
            current_host = getattr(self, 'hosts', {}).get(room)
            # 如果房主不存在且房间有成员，选择新房主
            if not current_host and self.rooms[room]:
                current_host = next(iter(self.rooms[room].keys()))
                self.hosts[room] = current_host
            # 构建房间更新消息
            room_update = {
                'type': 'room_update',
                'players': list(self.rooms[room].keys()),
                'host': current_host
            }
            # 广播给所有成员
            for pid, c in list(self.rooms[room].items()):
                try:
                    # 如果是房主变更消息，且当前玩家是新房主但不是原房主，添加host_changed标志
                    if current_host == pid and (not hasattr(self, '_last_hosts') or 
                        room not in self._last_hosts or self._last_hosts[room] != pid):
                        room_update['host_changed'] = True
                    else:
                        room_update['host_changed'] = False
                    c.send(json.dumps(room_update).encode())
                except:
                    pass
            # 更新上一次的房主记录
            if not hasattr(self, '_last_hosts'):
                self._last_hosts = {}
            self._last_hosts[room] = current_host

if __name__=='__main__':
    GameServer().start()
    print("[服务器] 运行中… Ctrl+C 退出")
    threading.Event().wait()
