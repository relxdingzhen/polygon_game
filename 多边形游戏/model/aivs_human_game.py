

class AIGame:
    def __init__(self, model):
        self.model = model  # 游戏模型
        self.ai_level = 1   # AI 难度等级

    def make_ai_move(self):
        """AI 的决策逻辑"""
        # 根据游戏状态，AI 决定下一步操作
        print("AI 做出决策...")

    def check_winner(self):
        """检查当前游戏是否有获胜者"""
        if self.model.get_winner():
            print("AI 或 玩家 获胜！")
            return True
        return False
