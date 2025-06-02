import os
import sys

import pandas as pd
import random
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QGroupBox, QApplication, QLabel, QSplitter,
                            QMainWindow)
from qfluentwidgets import (RadioButton, PushButton, TextEdit, InfoBar, FluentIcon,
                          SpinBox, ComboBox)
from PyQt5.QtWidgets import QCheckBox  # 导入复选框
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据抽取工具")
        self.resize(1200, 800)

        # 创建主界面
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # 初始化UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        # 上部分 - 选择区域
        top_group = QGroupBox('数据抽取设置')
        top_layout = QVBoxLayout(top_group)

        # 添加文件选择下拉框
        file_layout = QHBoxLayout()
        self.file_combo = ComboBox()
        self.file_combo.setMinimumWidth(200)
        self.refresh_btn = PushButton('刷新文件列表')
        self.refresh_btn.setIcon(FluentIcon.SYNC)
        self.open_folder_btn = PushButton('打开数据目录')
        self.open_folder_btn.setIcon(FluentIcon.FOLDER)

        file_layout.addWidget(self.file_combo)
        file_layout.addWidget(self.refresh_btn)
        file_layout.addWidget(self.open_folder_btn)
        file_layout.addStretch()

        # 更新文件列表
        self._update_file_list()

        # 单选按钮组
        radio_layout = QHBoxLayout()
        self.radio_fixed = RadioButton('定量选择')
        self.radio_random = RadioButton('随机选择')
        self.radio_fixed.setChecked(True)
        radio_layout.addWidget(self.radio_fixed)
        radio_layout.addWidget(self.radio_random)
        radio_layout.addStretch()

        # 输入区域
        input_layout = QHBoxLayout()
        self.fixed_input = SpinBox()
        self.fixed_input.setRange(1, 1000)
        self.fixed_input.setValue(100)

        self.random_min = SpinBox()
        self.random_max = SpinBox()
        self.random_min.setRange(1, 1000)
        self.random_max.setRange(1, 1000)
        self.random_min.setValue(50)
        self.random_max.setValue(150)

        # 添加随机数量显示标签
        self.random_count_label = QLabel('')

        self.random_min.hide()
        self.random_max.hide()
        self.random_count_label.hide()

        input_layout.addWidget(self.fixed_input)
        input_layout.addWidget(self.random_min)
        input_layout.addWidget(self.random_max)
        input_layout.addWidget(self.random_count_label)
        input_layout.addStretch()

        # 添加复选框：是否显示下一根12点K线的收盘价
        self.checkbox_12pm = QCheckBox('显示下一根12点K线的收盘价')
        top_layout.addWidget(self.checkbox_12pm)

        # 抽取按钮
        self.extract_btn = PushButton('抽取数据')
        self.extract_btn.setIcon(FluentIcon.DOWNLOAD)

        # 添加到top_layout
        top_layout.addLayout(file_layout)
        top_layout.addLayout(radio_layout)
        top_layout.addLayout(input_layout)
        top_layout.addWidget(self.extract_btn)

        # 下部分 - 显示区域
        bottom_layout = QHBoxLayout()

        # 左右分割器
        self.splitter = QSplitter(Qt.Horizontal)

        # 左侧文本框
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        data_label = QLabel('抽取的数据:')
        self.data_display = TextEdit()
        self.data_display.setReadOnly(True)
        left_layout.addWidget(data_label)
        left_layout.addWidget(self.data_display)

        # 右侧文本框
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        prediction_label = QLabel('下一根K线收盘价:')
        self.prediction_display = TextEdit()
        self.prediction_display.setReadOnly(True)
        self.copy_btn = PushButton('复制抽取数据')
        self.copy_btn.setIcon(FluentIcon.COPY)

        right_layout.addWidget(prediction_label)
        right_layout.addWidget(self.prediction_display)
        right_layout.addWidget(self.copy_btn)

        # 将左右两个小部件添加到分割器
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)

        # 添加分割器到底部布局
        bottom_layout.addWidget(self.splitter)

        # 添加到主布局
        self.main_layout.addWidget(top_group)
        self.main_layout.addLayout(bottom_layout)

    def _connect_signals(self):
        # 连接信号
        self.radio_fixed.toggled.connect(self._on_radio_toggled)
        self.radio_random.toggled.connect(self._on_radio_toggled)
        self.extract_btn.clicked.connect(self._on_extract)
        self.copy_btn.clicked.connect(self._on_copy)
        self.refresh_btn.clicked.connect(self._update_file_list)
        self.open_folder_btn.clicked.connect(self._open_data_folder)

    def _on_radio_toggled(self):
        if self.radio_fixed.isChecked():
            self.fixed_input.show()
            self.random_min.hide()
            self.random_max.hide()
            self.random_count_label.hide()
        else:
            self.fixed_input.hide()
            self.random_min.show()
            self.random_max.show()
            self.random_count_label.show()

    def _on_extract(self):
        try:
            # 获取选中的文件
            selected_file = self.file_combo.currentText()
            if not selected_file:
                self._show_error('请选择数据文件')
                return

            # 读取数据
            df = pd.read_csv(os.path.join('data_storage', selected_file))
            total_rows = len(df)

            # 确定抽取数量
            if self.radio_fixed.isChecked():
                # 定量抽取
                count = self.fixed_input.value()
                self.random_count_label.setText('')
            else:
                # 随机数量
                min_val = self.random_min.value()
                max_val = self.random_max.value()
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                count = random.randint(min_val, max_val)
                self.random_count_label.setText(f'本次抽取数量: {count}')

            # 确保不超过数据总量
            if count > total_rows - 1:  # -1确保有下一个数据点
                count = total_rows - 1

            # 随机选择起始点，然后获取连续数据
            start_idx = random.randint(0, total_rows - count - 1)
            selected_indices = list(range(start_idx, start_idx + count))

            # 获取选中的数据和下一个收盘价
            selected_data = df.iloc[selected_indices]
            next_prices = df.iloc[[i + 1 for i in selected_indices]]['close'].values

            # 显示数据
            self.data_display.setText(selected_data.to_string(index=False))

            # 判断是否勾选了“显示下一根12点K线的收盘价”
            if self.checkbox_12pm.isChecked():
                # 找到下一根12点K线的收盘价
                last_timestamp = df.iloc[selected_indices[-1]]['timestamp']
                next_12pm_price = self._find_next_12pm_price(df, last_timestamp)
                if next_12pm_price is not None:
                    self.prediction_display.setText(f"下一根12点K线收盘价：{next_12pm_price:.2f}")
                else:
                    self.prediction_display.setText("未找到下一根12点K线的收盘价")
            else:
                # 显示下一根K线的收盘价
                last_next_price = next_prices[-1]
                self.prediction_display.setText(f"下一根K线收盘价：{last_next_price:.2f}")

        except Exception as e:
            self._show_error(str(e))

    def _find_next_12pm_price(self, df, last_timestamp):
        """
        找到下一根12:00:00 K线的收盘价
        """
        # 将时间戳转换为 datetime 类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
        # 找到当前时间戳的下一个12:00:00 K线
        last_time = pd.to_datetime(last_timestamp)
        next_12pm_time = last_time + pd.Timedelta(hours=(12 - last_time.hour) % 12)
    
        # 确保时间是12:00:00
        if next_12pm_time.hour != 12:
            next_12pm_time = next_12pm_time + pd.Timedelta(hours=12)
    
        # 找到下一个12:00:00 K线的收盘价
        next_12pm_row = df[df['timestamp'] == next_12pm_time]
        if not next_12pm_row.empty:
            return next_12pm_row.iloc[0]['close']
        return None

    
    def _on_copy(self):
        # 复制左侧数据显示框的内容
        text = self.data_display.toPlainText()
        QApplication.clipboard().setText(text)
        InfoBar.success(
            title='成功',
            content='已复制抽取数据',
            parent=self
        )
    
    def _show_error(self, message):
        InfoBar.error(
            title='错误',
            content=message,
            parent=self
        )
    
    def _update_file_list(self):
        """更新文件列表"""
        self.file_combo.clear()
        try:
            data_files = [f for f in os.listdir('data_storage') 
                         if f.endswith('.csv')]
            if data_files:
                self.file_combo.addItems(data_files)
                self.file_combo.setCurrentIndex(0)
            else:
                self._show_error('数据文件夹为空')
        except Exception as e:
            self._show_error(f'读取文件列表失败: {str(e)}')
    
    def _open_data_folder(self):
        """打开数据文件夹"""
        try:
            folder_path = os.path.abspath('data_storage')
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS 和 Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', folder_path])
            
            InfoBar.success(
                title='成功',
                content='已打开数据目录',
                parent=self
            )
        except Exception as e:
            self._show_error(f'打开数据目录失败: {str(e)}')
