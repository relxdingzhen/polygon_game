# main.py
import sys
from view.main_page import MainPage  # 导入主页面

def main():
    # 获取命令行参数
    client_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    # 启动主菜单
    main_page = MainPage()

    main_page.title(f"多边形游戏 - 客户端 {client_id}")  # 设置不同的窗口标题
    main_page.mainloop()  # 启动主菜单

if __name__ == "__main__":
    main()
