import copy
import random


class PolyModel:
    def __init__(self):
        self.vertices = []
        self.operators = []
        self.history = []
        self.redo_stack = []
        self.current_step = -1

    def initialize(self, n, vertices=None, operators=None, min_val=-10, max_val=10):
        """初始化游戏数据
        Args:
            min_val: 随机生成时的最小值
            max_val: 随机生成时的最大值
        """
        if vertices and operators:  # 手动输入模式
            if len(vertices) != n or len(operators) != n:
                raise ValueError("输入数据维度不匹配")
            self.vertices = vertices
            self.operators = [op.replace('×', '*') for op in operators]  # 转换符号
        else:  # 随机生成模式
            self.vertices = [random.randint(min_val, max_val) for _ in range(n)]
            self.operators = [random.choice(['+', '*']) for _ in range(n)]

        # 初始化历史记录
        self.history = [{"vertices": copy.deepcopy(self.vertices),
                         "operators": copy.deepcopy(self.operators)}]
        self.current_step = 0
        self.redo_stack = []

    def merge_vertices(self, edge_index):
        prev_vertices = copy.deepcopy(self.vertices)
        prev_operators = copy.deepcopy(self.operators)

        try:
            if edge_index >= len(self.operators):
                raise IndexError("无效边索引")

            # 记录被合并的顶点信息
            merged_indices = (edge_index, (edge_index + 1) % len(self.vertices))
            v1 = self.vertices[merged_indices[0]]
            v2 = self.vertices[merged_indices[1]]
            op = self.operators[edge_index]

            # 执行合并操作
            self.operators.pop(edge_index)
            self.vertices.pop(merged_indices[0])
            self.vertices.pop(merged_indices[0] % len(self.vertices))  # 处理环形结构
            new_val = v1 + v2 if op == '+' else v1 * v2
            self.vertices.insert(edge_index, new_val)

            # 保存合并记录
            merge_info = {
                'indices': merged_indices,
                'values': (v1, v2),
                'operator': op,
                'result': new_val
            }

            if prev_vertices != self.vertices:
                self.save_state(merge_info)

            return True
        except Exception as e:
            self.vertices = prev_vertices
            self.operators = prev_operators
            return False

    def save_state(self, merge_info=None):
        """保存状态并记录合并信息"""
        new_state = {
            'vertices': copy.deepcopy(self.vertices),
            'operators': copy.deepcopy(self.operators),
            'merge_info': merge_info  # 新增合并信息字段
        }

        # 去重检查（保持原有逻辑）
        if self.history and self.current_step >= 0:
            last_state = self.history[self.current_step]
            if (last_state['vertices'] == new_state['vertices'] and
                    last_state['operators'] == new_state['operators']):
                return

        # 保存状态（保持原有截断逻辑）
        self.history = self.history[:self.current_step + 1]
        self.history.append(new_state)
        self.current_step = len(self.history) - 1
        self.redo_stack.clear()

    def undo(self):
        if self.current_step > 0:
            # 把当前状态存入重做栈
            self.redo_stack.append({
                "vertices": copy.deepcopy(self.vertices),
                "operators": copy.deepcopy(self.operators)
            })

            # 回退到上一步
            self.current_step -= 1
            prev_state = self.history[self.current_step]

            # 更新当前数据
            self.vertices = copy.deepcopy(prev_state["vertices"])
            self.operators = copy.deepcopy(prev_state["operators"])
            return True
        return False

    def redo(self):
        if self.redo_stack:
            # 获取重做状态
            recovered_state = self.redo_stack.pop()

            # 更新模型状态
            self.vertices = copy.deepcopy(recovered_state["vertices"])
            self.operators = copy.deepcopy(recovered_state["operators"])

            # 更新历史记录
            self.current_step += 1
            if self.current_step >= len(self.history):
                self.history.append(recovered_state)
            else:
                self.history[self.current_step] = recovered_state
            return True
        return False

    def get_max_score_with_steps(self):
        """返回最大得分和计算步骤"""
        n = len(self.vertices)
        if n == 0:
            return 0, []
        if n == 1:
            return self.vertices[0], ["单个顶点直接取值: {}".format(self.vertices[0])]

        # 扩展数组处理环形结构
        nums = self.vertices * 2
        ops = self.operators * 2
        dp_max = [[-float('inf')] * (2 * n) for _ in range(2 * n)]
        dp_min = [[float('inf')] * (2 * n) for _ in range(2 * n)]
        step_log = []

        # 初始化日志
        step_log.append("初始化动态规划表:")
        for i in range(2 * n):
            dp_max[i][i] = nums[i]
            dp_min[i][i] = nums[i]
            step_log.append(f"dp_max[{i}][{i}] = {nums[i]}, dp_min[{i}][{i}] = {nums[i]}")

        step_log.append("\n开始动态规划计算:")
        for length in range(1, n):
            step_log.append(f"\n计算长度为 {length} 的子区间:")
            for i in range(2 * n - length):
                j = i + length
                step_log.append(f"\n处理区间 [{i}, {j}]:")

                for k in range(i, j):
                    op = ops[k]
                    step_log.append(f"  分割点 k={k}，运算符 '{op}'")

                    # 获取子区间极值
                    a = dp_max[i][k]
                    b = dp_max[k + 1][j]
                    c = dp_min[i][k]
                    d = dp_min[k + 1][j]

                    if op == '+':
                        max_val = a + b
                        min_val = c + d
                        step_log.append(f"   加法：max({a}+{b})={max_val}, min({c}+{d})={min_val}")
                    else:
                        candidates = [a * b, a * d, c * b, c * d]
                        max_val = max(candidates)
                        min_val = min(candidates)
                        step_log.append(
                            f"   乘法：候选值({a}*{b}, {a}*{d}, {c}*{b}, {c}*{d}) => max={max_val}, min={min_val}")

                    # 更新极值
                    if max_val > dp_max[i][j]:
                        dp_max[i][j] = max_val
                        step_log.append(f"   更新dp_max[{i}][{j}] = {max_val}")
                    if min_val < dp_min[i][j]:
                        dp_min[i][j] = min_val
                        step_log.append(f"   更新dp_min[{i}][{j}] = {min_val}")

        # 收集最终结果
        step_log.append("\n最终计算结果:")
        max_vals = [dp_max[i][i + n - 1] for i in range(n)]
        final_max = max(max_vals)
        step_log.append(f"各起点最大值列表: {max_vals}")
        step_log.append(f"全局最大值: {final_max}")

        return final_max, step_log
