from model.aivs_human_game import AIGame
from view.aivs_human_page import AIVsHumanPage

class AIVsHumanPresenter:
    def __init__(self, view):
        self.view = view
        self.model = AIGame()

    def make_ai_move(self):
        self.model.make_ai_move()  # 让 AI 做出决策
        self.view.update_game_status("AI 已做出决策")

    def check_for_winner(self):
        if self.model.check_winner():
            self.view.show_winner("AI 或 玩家 获胜！")
