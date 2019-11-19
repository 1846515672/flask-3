"""
模型定义
"""
from text import db



class Model(db.Model):
    __abstract__ = True #代表当前类为抽象类，不会再继承过程当中执行
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        session = db.session()
        session.add(self)
        session.commit()

    def delete(self):
        session = db.session()
        session.delete(self)
        session.commit()

class User(Model):
    nick_name = db.Column(db.String(32))
    email = db.Column(db.String(32))
    password = db.Column(db.String(32))

class Label(Model):
    l_name = db.Column(db.String(32))  # 标签名称
    description = db.Column(db.Text)  # 标签描述
    c_label = db.relationship("Course",backref="class_label")

    def __repr__(self):
        return self.l_name

class Course(Model):
    c_name = db.Column(db.String(32)) #课程名称
    description = db.Column(db.Text)  #课程描述
    picture = db.Column(db.String(32))  #课程logo
    show_number = db.Column(db.Integer)  #观看人数
    c_time_number = db.Column(db.Integer) #课时
    state = db.Column(db.Integer,default = 1) #课程状态 0 即将上线  1上线 默认为 1
    c_type = db.Column(db.Integer,default = 0) #课程类型 0免费  1限时免费  2 VIP会员  默认免费
    label_id = db.Column(db.Integer,db.ForeignKey("label.id"))

    def __repr__(self):
        return self.c_name

