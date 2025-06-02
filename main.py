import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == '__main__':
    # 确保数据存储目录存在
    if not os.path.exists('data_storage'):
        os.makedirs('data_storage')
        
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 