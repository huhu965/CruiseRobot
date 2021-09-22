from PyQt5.QtWidgets import QGridLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox

class start_navigate_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("开始导航")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        self.lab_map_name = QLabel("地图名称")
        self.edit_map_name = QLineEdit()
        self.lab_position_name = QLabel("标记点名称")
        self.edit_position_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_map_name , 1 , 0)
        self.glayout.addWidget(self.edit_map_name , 1 , 1)
        self.glayout.addWidget(self.lab_position_name , 2 , 0)
        self.glayout.addWidget(self.edit_position_name , 2 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)

    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"map_name": str(self.edit_map_name.text()),
                "position_name": str(self.edit_position_name.text())
                }

class add_navigate_task_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("添加导航点")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        self.lab_map_name = QLabel("序号:(不填默认追加在末尾)")
        self.edit_map_name = QLineEdit()
        self.lab_position_name = QLabel("标记点名称")
        self.edit_position_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_map_name , 1 , 0)
        self.glayout.addWidget(self.edit_map_name , 1 , 1)
        self.glayout.addWidget(self.lab_position_name , 2 , 0)
        self.glayout.addWidget(self.edit_position_name , 2 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)

    def get_param(self):                 #   定义获取用户输入数据的方法
        if self.edit_map_name.text() == '':
            number = 0
        else:
            number = int(self.edit_map_name.text())
        return {"number": number,
                "position_name": str(self.edit_position_name.text())
                }

class delect_task_point_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("删除导航点")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        self.lab_map_name = QLabel("序号:(不填默认删除第一个任务)")
        self.edit_map_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_map_name , 1 , 0)
        self.glayout.addWidget(self.edit_map_name , 1 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)

    def get_param(self):                 #   定义获取用户输入数据的方法
        if self.edit_map_name.text() == '':
            number = 0
        else:
            number = int(self.edit_map_name.text())
        return {"number": number}