# main.py
from view.main_page import MainPage  # 导入主页面

def main():
    # 启动主菜单
    main_page = MainPage()
    main_page.mainloop()  # 启动主菜单

if __name__ == "__main__":
    main()
