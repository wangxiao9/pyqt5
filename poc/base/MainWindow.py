import datetime
import logging
import sys

from PyQt5 import uic
from os import path

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication

from utils.helper import ConfigsParser



class NMainWindow:

    def __init__(self):
        self.ui = uic.loadUi('./layout/nautilus.ui')
        self.logger = Log().get_log()
        self.config = ConfigsParser()
        handler = ConsolePanelHandler(self)
        self.logger.addHandler(handler)
        # for i in range(100):
        #     self.logger.error("测试错误")
        #     self.logger.warning("警告")
        #     self.logger.info("正常")


        # self.ui.actionExit.triggered.connect(self.exit)

    def write(self, logs):
        self.ui.logs_text.append(logs)
        self.ui.logs_text.moveCursor(QTextCursor.End)  # 光标末尾
        self.ui.logs_text.moveCursor(QTextCursor.StartOfLine)

    def exit(self):
        self.ui.close()


class ConsolePanelHandler(logging.Handler):

    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.parent = parent

    def emit(self, record):
        """输出格式可以按照自己的意思定义HTML格式"""
        record_dict = record.__dict__
        asctime = record_dict['asctime'] + " >> "
        line = record_dict['filename'] + " -> line:" + str(record_dict['lineno']) + " | "
        levelname = record_dict['levelname']
        message = record_dict['message']
        if levelname == 'ERROR':
            color = "#FF0000"
        elif levelname == 'WARNING':
            color = "#FFD700"
        else:
            color = "#008000"
        html = f'''
        <div >
            <span>{asctime}</span>
            <span style="color:#4e4848;">{line.upper()}</span>
            <span style="color: {color};">{levelname}</span>
            <span style="color:	#696969;">{message}</span>
        </div>
        '''
        self.parent.write(html)  # 将日志信息传给父类 write 函数 需要在父类定义一个函数

class Log:
    def __init__(self, ):
        otherStyleTime = datetime.datetime.now().strftime("%Y-%m-%d")  # "%Y-%m-%d-%H-%M-%S"
        user_path = f"{path.expanduser('~')}\\logs"
        log_path = f"{user_path}\\{otherStyleTime}.log"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=20)
        file_log = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s >> (%(filename)s[line:%(lineno)d]) | %(levelname)s: %(message)s - ',
                                      '%Y-%m-%d %H:%M:%S')
        file_log.setFormatter(formatter)
        self.logger.addHandler(file_log)

    def get_log(self):
        return self.logger

