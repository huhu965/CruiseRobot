from generl_function import respond_message_cerat

def position(self,param = ""):
    try:
        response = requests.get(f"http://{self.robot_ip}:{self.robot_port}/gs-robot/real_time_data/position", timeout=1)
        back_data = respond_message_cerat(content=response.content)
    except Exception as e:
        back_data = respond_message_cerat(errorCode = f"get request error:{e}",msg = "fail", successed= False)
    finally:
        return back_data