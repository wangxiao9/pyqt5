import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit
from PyQt5.QtGui import QFont
import pandas as pd
from openpyxl import Workbook

from main import DiffExcel


class ExcelComparator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("diff Comparator")
        self.setGeometry(100, 100, 700, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.file1_label = QLabel("Target File:")
        self.layout.addWidget(self.file1_label)

        self.file1_button = QPushButton("Upload File 1")
        self.file1_button.clicked.connect(self.upload_file1)
        self.layout.addWidget(self.file1_button)

        self.file2_label = QLabel("Reference File:")
        self.layout.addWidget(self.file2_label)

        self.file2_button = QPushButton("Upload File 2")
        self.file2_button.clicked.connect(self.upload_file2)
        self.layout.addWidget(self.file2_button)

        self.field_labbel = QLabel("Configure Compare Field:")
        self.layout.addWidget(self.field_labbel)

        # 创建一个表单布局
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        # 添加自定义配置字段
        self.add_config_field("Field 1:")
        self.add_config_field("Field 2:")

        # 创建一个按钮
        add_button = QPushButton("Add Field")
        add_button.clicked.connect(self.add_field_button_clicked)
        self.layout.addWidget(add_button)
        add_button.setEnabled(False)

        self.compare_button_label = QLabel("Function:")
        self.layout.addWidget(self.compare_button_label)

        self.compare_button = QPushButton("Compare")
        self.compare_button.clicked.connect(self.compare_files)
        self.layout.addWidget(self.compare_button)

        self.export_button = QPushButton("Export Result")
        self.export_button.clicked.connect(self.export_result)
        self.layout.addWidget(self.export_button)

        self.result_label = QLabel("Comparison Result:")
        self.layout.addWidget(self.result_label)

        self.result_table = QTableWidget()
        self.layout.addWidget(self.result_table)

        self.central_widget.setLayout(self.layout)
        self.compare_field = {}

    def get_content(self):

        # 遍历布局中的所有项
        # for i in range(self.form_layout.count()):
        #     item = self.form_layout.itemAt(i)
        #     # 获取项中的小部件
        #     widget = item.widget()
        #
        #     # 如果小部件是标签或文本框，则打印其文本内容
        #     if isinstance(widget, QLabel) or isinstance(widget, QLineEdit):
        #         print(widget.text())

        for row in range(self.form_layout.rowCount()):
            item = self.form_layout.itemAt(row, QFormLayout.FieldRole)
            if item and isinstance(item.widget(), QLineEdit):
                line_edit = item.widget()
                content = line_edit.text()
                self.compare_field[f"Field {row + 1}"] = content

    def add_config_field(self, label_text):
        # 创建标签和文本框
        label = QLabel(label_text)
        line_edit = QLineEdit()

        # 将标签和文本框添加到表单布局中
        self.form_layout.addRow(label, line_edit)

    def add_field_button_clicked(self):
        # 获取当前字段数量
        field_count = self.form_layout.rowCount()

        # 添加新的字段
        self.add_config_field(f"Field {field_count + 1}:")

    def upload_file1(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload File 1", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            self.file1_label.setText("File 1: " + file_name)
            self.file1_path = file_name

    def upload_file2(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload File 2", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            self.file2_label.setText("File 2: " + file_name)
            self.file2_path = file_name

    def compare_files(self):
        self.get_content()
        # print(self.compare_field)
        try:
            diff_obj = DiffExcel(self.file1_path, self.file2_path, self.compare_field)
            add, remove, change, new, old = diff_obj.sort()
            row = max(len(add), len(remove), len(change))
        except  Exception as e:
            self.result_table.setItem(0, 0, QTableWidgetItem("Error: " + str(e)))

        try:
            self.result_table.clear()
            self.result_table.setRowCount(row)
            self.result_table.setColumnCount(5)
            self.result_table.setHorizontalHeaderLabels(["Add", "Remove", "Change", "New_Value","Old_Value"])

            for i in range(len(add)):
                self.result_table.setItem(i, 0, QTableWidgetItem(add[i]))

            for j in range(len(remove)):
                self.result_table.setItem(j, 1, QTableWidgetItem(remove[j]))


            for k in range(len(change)):
                self.result_table.setItem(k, 2, QTableWidgetItem(change[k]))
                self.result_table.setItem(k, 3, QTableWidgetItem(str(new[k])))
                self.result_table.setItem(k, 4, QTableWidgetItem(str(old[k])))
        except Exception as e:
            self.result_table.clear()
            self.result_table.setRowCount(1)
            self.result_table.setColumnCount(1)
            self.result_table.setItem(0, 0, QTableWidgetItem("Error: " + str(e)))

    def export_result(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Export Result", "", "Excel Files (*.xlsx)")
            if file_name is None:
                file_name = 'compare.xlsx'
                # 创建一个新的Excel工作簿
            workbook = Workbook()

                # 获取当前活动的工作表
            worksheet = workbook.active
            for row in range(self.result_table.rowCount()):
                for col in range(self.result_table.columnCount()):
                    item = self.result_table.item(row, col)
                    if item is not None:
                        worksheet.cell(row=row + 1, column=col + 1).value = item.text()
                workbook.save(file_name)
        except Exception as e:
            print("Error: " + str(e))



        # 保存Excel文件

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelComparator()
    window.show()
    sys.exit(app.exec_())
