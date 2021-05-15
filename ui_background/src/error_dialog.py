from PyQt5.QtWidgets import QGridLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox

class message_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self,message_type,message):
        super().__init__()
        self.message = message
        self.message_type = message_type
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.message_type)      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_message = QLabel(self.message) 
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
 
        self.setLayout(self.glayout)