from linebot.models.send_messages import TextSendMessage
from transitions.extensions import GraphMachine
from werkzeug.local import F
from utils import send_text_message
from app import College, Course, Dept
import json
import re
class TocMachine(GraphMachine):
    def __init__(self, uid, **machine_configs):
        self.machine = GraphMachine(model=self,**machine_configs)
        self.uid = uid
        self.dept = ''

    def is_entering_coll(self, event):
        text = event.message.text
        return text.lower() == "query"

    def is_entering_dept(self, event):
        text = event.message.text
        if not re.compile('[0-9]*').match(text).group():
            return False
        return int(text) in range(len(College.query.all()))

    def is_entering_mand(self, event):
        text = event.message.text
        deptList = Dept.query.all()
        idList = []
        for dept in deptList:
            idList.append(dept.id)
        
        return text in idList

    def is_entering_result(self, event):
        text = event.message.text
        return text.upper() in ["M", "O", "A"]

    def is_returing_init(self, event):
        text = event.message.text
        return text.lower() == "exit"

    def on_enter_coll(self, event):
        print("I'm entering coll")

        collList = College.query.all()
        reply = "請輸入[ ]中的數字"
        for coll in collList:
            reply = f'{reply}\n[{coll.id}] {coll.name}'
        reply_token = event.reply_token
        send_text_message(reply_token, reply)

    def on_enter_dept(self, event):
        print("I'm entering dept")
        collID = int(event.message.text)
        deptIDList = json.loads(College.query.get(collID).depts)
        reply = "請輸入[ ]中的系所代號"
        for deptID in deptIDList:
            dept = Dept.query.get(deptID)
            reply = f'{reply}\n[{dept.id}] {dept.name}'

        reply_token = event.reply_token
        send_text_message(reply_token, reply)

    def on_enter_mand(self, event):
        self.dept = event.message.text
        print("I'm entering mand")
        reply = "要查詢必修(M), 選修(O), 所有(A)?\n"
        reply_token = event.reply_token
        send_text_message(reply_token, reply)

    def on_enter_result(self, event):
        print("Leaving mand")
        text = event.message.text.upper()
        reply = "欲查詢課程如下:"
        if text.upper() == "M":
            courList = Course.query.filter(
                Course.id.startswith(self.dept),
                Course.mandatoriness == True
            ).all()
        elif text.upper() == "O":
            courList = Course.query.filter(
                Course.id.startswith(self.dept),
                Course.mandatoriness == False
            ).all()
        else:
            courList = Course.query.filter(Course.id.startswith(self.dept)).all()
        for cour in courList:
            reply = f'{reply}\n{cour.name}'
        
        reply_token = event.reply_token
        send_text_message(reply_token, reply)
        self.go_init()

