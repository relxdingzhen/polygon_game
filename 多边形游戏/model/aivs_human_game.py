# model/aivs_human_game.py
import copy
import random

class AIModel:
    """棋盘模型 + 动态规划求最大得分"""
    def __init__(self,difficulty='hard'):
        self.vertices = []
        self.operators = []
        self.history = []
        self.difficulty = difficulty

    # ---------- 初始化 ----------
    def initialize(self, n, vertices=None, operators=None,
                   min_val=-10, max_val=10):
        if vertices and operators:
            self.vertices = list(vertices)
            self.operators = [op.replace('×', '*') for op in operators]
        else:
            self.vertices = [random.randint(min_val, max_val) for _ in range(n)]
            self.operators = [random.choice(['+', '*']) for _ in range(n)]

        self.history = [{"vertices": copy.deepcopy(self.vertices),
                         "operators": copy.deepcopy(self.operators)}]

    # ---------- 合并操作 ----------
    def merge_vertices(self, edge_idx: int) -> bool:
        if edge_idx >= len(self.operators):           # 非法索引
            return False

        v1_idx = edge_idx
        v2_idx = (edge_idx + 1) % len(self.vertices)

        v1, v2 = self.vertices[v1_idx], self.vertices[v2_idx]
        op = self.operators.pop(edge_idx)

        new_val = v1 + v2 if op == '+' else v1 * v2
        # 删除旧顶点并插入新顶点
        if v2_idx > v1_idx:
            self.vertices.pop(v2_idx)
            self.vertices.pop(v1_idx)
        else:  # 环形情况下先删大的索引
            self.vertices.pop(v1_idx)
            self.vertices.pop(v2_idx)
        self.vertices.insert(edge_idx, new_val)

        # 记录历史便于调试（对战版不做撤销）
        self.history.append({
            "vertices": copy.deepcopy(self.vertices),
            "operators": copy.deepcopy(self.operators)
        })
        return True
    #-----------四种方案的具体实现---------------
    #easy-随机策略
    def _random_strategy(self):
        return random.randint(0, len(self.operators) - 1)

    #easy++-最大值贪心策略
    def _max_greedy_strategy(self):
        best_idx, best_val = 0, -float('inf')
        for i in range(len(self.operators)):
            a, b = self.vertices[i], self.vertices[(i + 1) % len(self.vertices)]
            val = a + b if self.operators[i] == '+' else a * b
            if val > best_val:
                best_val = val
                best_idx = i
        return best_idx

    #medium-2步前瞻
    def _two_step_lookahead(self):
        best_score, best_idx = -float('inf'), 0
        for i in range(len(self.operators)):
            tmp = copy.deepcopy(self)
            if not tmp.merge_vertices(i): continue
            for j in range(len(tmp.operators)):
                tmp2 = copy.deepcopy(tmp)
                if not tmp2.merge_vertices(j): continue
                score = tmp2.vertices[0] if len(tmp2.vertices) == 1 else sum(tmp2.vertices)
                if score > best_score:
                    best_score = score
                    best_idx = i
        return best_idx

    #hard-模拟➕DP
    def _simulate_with_dp(self):
        best_score, best_idx = -float('inf'), 0
        for i in range(len(self.operators)):
            tmp = copy.deepcopy(self)
            if not tmp.merge_vertices(i): continue
            score, _ = tmp.get_max_score_with_steps()
            if score > best_score:
                best_score = score
                best_idx = i
        return best_idx

    #hard++-蒙特卡洛树搜索简化版
    def _mcts_simulation(self, sim_times=10):
        def simulate_once(model):
            tmp = copy.deepcopy(model)
            while len(tmp.vertices) > 1:
                idx = random.randint(0, len(tmp.operators) - 1)
                tmp.merge_vertices(idx)
            return tmp.vertices[0]

        best_score, best_idx = -float('inf'), 0
        for i in range(len(self.operators)):
            scores = []
            for _ in range(sim_times):
                tmp = copy.deepcopy(self)
                if not tmp.merge_vertices(i): continue
                scores.append(simulate_once(tmp))
            avg = sum(scores) / len(scores) if scores else -float('inf')
            if avg > best_score:
                best_score = avg
                best_idx = i
        return best_idx

    # ---------- AI 选边：五种难度选择----------
    def get_best_edge(self) -> int:
        if len(self.vertices) <= 1:
            return 0

        if self.difficulty == 'easy':
            return self._random_strategy()

        elif self.difficulty == 'easy++':
            return self._max_greedy_strategy()

        elif self.difficulty == 'medium':
            return self._two_step_lookahead()

        elif self.difficulty == 'hard':
            return self._simulate_with_dp()

        elif self.difficulty == 'hard++':
            return self._mcts_simulation()

        else:
            return self._simulate_with_dp()  # 默认 fallback

    # ---------- 动态规划求环形最大得分 ----------
    def get_max_score_with_steps(self):
        """返回(最大得分, 日志列表)；日志主要给“最优解”弹窗查看"""
        n = len(self.vertices)
        if n == 1:
            return self.vertices[0], [f"单顶点值 = {self.vertices[0]}"]

        # 展开环形 → 线性 DP
        A = self.vertices * 2
        O = self.operators * 2
        dp_max = [[-float('inf')] * (2*n) for _ in range(2*n)]
        dp_min = [[ float('inf')] * (2*n) for _ in range(2*n)]

        for i in range(2*n):
            dp_max[i][i] = dp_min[i][i] = A[i]

        log = []
        for L in range(1, n):              # 区间长度
            for i in range(0, 2*n-L):
                j = i + L
                for k in range(i, j):
                    op = O[k]
                    a, b = dp_max[i][k], dp_max[k+1][j]
                    c, d = dp_min[i][k], dp_min[k+1][j]
                    if op == '+':
                        high, low = a + b, c + d
                    else:
                        cand = [a*b, a*d, c*b, c*d]
                        high, low = max(cand), min(cand)
                    dp_max[i][j] = max(dp_max[i][j], high)
                    dp_min[i][j] = min(dp_min[i][j], low)

        candidates = [dp_max[i][i+n-1] for i in range(n)]
        return max(candidates), log  # 省略中间日志以节省内存
