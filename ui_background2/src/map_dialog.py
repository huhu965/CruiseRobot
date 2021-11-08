from PyQt5.QtWidgets import QGridLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox

class new_map_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self,):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("新建地图")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入地图名称")
        # 用于接收用户输入的单行文本输入框
        self.edit_name = QLineEdit()   
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)

    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"map_name":str(self.edit_name.text()),
                "type":"0"
                }

class extend_map_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("扩展地图")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入地图名称")
        # 用于接收用户输入的单行文本输入框
        self.edit_name = QLineEdit()   
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)

    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"map_name":str(self.edit_name.text()),
                "type":"1"
                }

class load_map_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("加载地图")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入地图名称") 
        self.edit_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)
    
    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"map_name": str(self.edit_name.text())
                }

class delete_map_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("删除地图")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入地图名称") 
        self.edit_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)
    
    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"map_name": str(self.edit_name.text())
                }