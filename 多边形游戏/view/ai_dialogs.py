from view.dialogs import *

class AIHistoryDialog(HistoryDialog):
    def __init__(self, parent, presenter, mode='all'):
        super().__init__(parent, presenter, mode)
        self.title("AI 对战 - 操作历史记录")

    def format_step(self, step, step_num):
        """重写格式化方式：突出显示AI/玩家行为等"""
        content = f"步骤 {step_num}:\n"
        actor = step.get("actor", "未知")  # 假设step里加了 'actor': 'AI' 或 'Player'
        content += f"操作者: {actor}\n"
        content += f"顶点数: {len(step['vertices'])}\n"

        if 'merge_info' in step and step['merge_info']:
            info = step['merge_info']
            content += "┌── 合并详情 ──┐\n"
            content += f"│ {info['indices'][0] + 1}号({info['values'][0]}) "
            content += f"和 {info['indices'][1] + 1}号({info['values'][1]})\n"
            content += f"│ 运算符: {info['operator']}\n"
            content += f"│ 结果值: {info['result']}\n"
            content += "└────────────┘\n"
        else:
            content += "状态类型: 初始配置\n"

        content += f"当前顶点: {', '.join(map(str, step['vertices']))}\n"
        if len(step['operators']) > 0:
            content += f"剩余运算符: {' → '.join(step['operators'])}\n"

        # AI 特有内容（比如信心值或路径）
        if actor == 'AI' and 'ai_decision' in step:
            decision = step['ai_decision']
            content += f"AI 选择理由: {decision.get('reason', '未知')}\n"
            content += f"评估值: {decision.get('score', 'N/A')}\n"

        content += "━" * 40 + "\n"
        return content
