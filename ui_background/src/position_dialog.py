from PyQt5.QtWidgets import QGridLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox

class add_position_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("添加标记点")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入添加点的名称") 
        self.edit_name = QLineEdit()
        self.lab_explai_type = QLabel("1 2 3 4")
        self.lab_type = QLabel("请输入标记点的类型") 
        self.edit_type = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.lab_explai_type , 2 , 0)
        self.glayout.addWidget(self.lab_type , 3 , 0)
        self.glayout.addWidget(self.edit_type , 3 , 1)
        self.glayout.addWidget(self.buttons,5,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)
    
    def get_param(self):                 #   定义获取用户输入数据的方法
        return {"position_name": str(self.edit_name.text()),
                "type": int(self.edit_type.text())
                }
    def get_param_map_add(self):                 #   定义获取用户输入数据的方法
        return {"name": str(self.edit_name.text()),
                "type": int(self.edit_type.text())
                }

class delete_position_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("删除标记点")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_map_name = QLabel("标记点所在地图名称")
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

class get_angle_Dialog(QDialog):        #继承QDialog类,自定义对话窗口
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle("获取导航点角度")      # 窗口标题
        self.setGeometry(500,500,200,200)   # 窗口位置与大小
 
        #提示标签
        self.lab_name = QLabel("请输入导航点角度，正负180°") 
        self.edit_name = QLineEdit()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
 
        self.glayout = QGridLayout()
 
        self.glayout.addWidget(self.lab_name , 1 , 0)
        self.glayout.addWidget(self.edit_name , 1 , 1)
        self.glayout.addWidget(self.buttons,3,1)
 
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
        self.setLayout(self.glayout)
    
    def get_param(self):                 #   定义获取用户输入数据的方法
        try:
            angle = int(self.edit_name.text()) % 360
            if angle > 180:
                angle = angle - 360   
            return angle
        except Exception as e:
            print(e)
            angle = "error"
            return angle