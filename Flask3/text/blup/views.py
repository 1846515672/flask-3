"""
视图文件
"""
from text.zsq import LoginValid
from text.blup.form import UserForm
from flask_restful import Resource, Api
from flask import request
from flask import Response
from flask import session
import random
from text.models import *
from sqlalchemy import and_
from flask import redirect
import hashlib, os
from text.blup import lou_app
from flask import render_template
# from text import api


api = Api(lou_app)
class CourseApi(Resource):
    def __init__(self):
        self.result = {
            "virsion": "v1",
            "code": "200",
            "data": [],
            "methods": "",
            "pageiation": {}
        }
        self.page_size = 15 #一页展示页数
    def to_dict(self, obj):
        query_str = str(obj.query).split("SELECT")[1].split("FROM")[0].strip()
        key_list = [k.split(" AS ")[1].replace("course_", "") for k in query_str.split(",")]
        obj_to_dict = dict(
            zip(key_list, [getattr(obj, key) for key in key_list])
        )
        return obj_to_dict
    def get(self, id=None, page=None, page_num=None, field=None, value=None):
        if id:
            course_list = Course.query.get(int(id))
            data = self.to_dict(course_list)
            self.result["data"].append(data)
        else:
            #如果启用分页
            if page == "page":
                page_obj = Course.query.order_by(db.desc("id")).paginate(int(page_num), self.page_size) # 第一个参数是页码，第二个参数每页条数
                if field and str(value):
                    dicts = {field: value}
                    page_obj = Course.query.filter_by(**dicts).paginate(int(page_num)), self.page_size
                self.result["pageiation"]["has_next"] = page_obj.has_next
                self.result["pageiation"]["has_prev"] = page_obj.has_prev
                self.result["pageiation"]["next_num"] = page_obj.next_num
                self.result["pageiation"]["page"] = page_obj.page
                self.result["pageiation"]["pages"] = list(range(1,page_obj.pages+1))
                self.result["pageiation"]["per_page"] = page_obj.per_page
                self.result["pageiation"]["prev_num"] = page_obj.prev_num
                self.result["pageiation"]["total"] = page_obj.total
                course_list = page_obj.items
                course_list = page_obj.items
            else:
            # 如果有过滤条件，就按照过滤条件查询否则返回所有数据
                if field and str(value):
                    dicts = {field: value}
                    course_list = Course.query.filter_by(**dicts).all()
                else:
                    course_list = Course.query.all()
            self.result["data"] = [self.to_dict(i) for i in course_list]
        self.result["methods"] = request.method
        return self.result

    def post(self):
        self.result["methods"] = request.method
        return self.result

    def put(self, id):
        self.result["methods"] = request.method
        return self.result

    def delete(self, id):
        self.result["methods"] = request.method
        return self.result

api.add_resource(
      CourseApi,
    "/CourseApi/",
    "/CourseApi/<int:id>/",
    "/CourseApi/<string:field>/<string:value>/",
    "/CourseApi/<string:field>/<string:value>/<string:page>/<int:page_num>/",
    "/CourseApi/page/<string:page>/<int:page_num>/"
)#注意这里的(冒号):后面不要给空格!!!


@lou_app.route("/page_1/", methods=["GET", "POST"])
def paee_1():
    user = UserForm()#前端展示表单
    if request.method == "POST":
        user = UserForm(request.form) #将请求的数据传入表单类
        if user.validate(): #镜像校验,如果成功,进行数据保存
            post_data = user.data
            message = "保存数据库"
        else:
            message = user.errors #失败后,会通过校验实例返回错误
    return render_template("1.html", **locals())


@lou_app.route("/page_2/")
@lou_app.route("/page_2/<int:id>/")
def page_2(id=1):
    return "id is %s"%id


@lou_app.route("/", methods=["get","post"])
def index():
    register = request.args.get("register")
    if request.method == "POST":
        username = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User()
        user.nick_name = username
        user.password = set_password(password)
        user.email = email
        user.save()
        register = True
    response = Response(render_template("index.html", **locals()))
    return response


def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


@lou_app.route("/login/",methods=["get","post"])
def login():
    response = redirect("/") #跳转回首页
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email = email).first()
        if user:
            request_password = set_password(password)
            if request_password == user.password:
                response.set_cookie("email", user.email)
    return response


@lou_app.route("/logout/")
def logout():
    response = redirect("/")
    response.delete_cookie("email")
    return response


@lou_app.route("/courses/index/<path:url_arg>/")
@LoginValid
def courses_index(url_arg):
    # 获取label，固定
    label_list = Label.query.all()
    # 获取url上匹配的过滤条件，并且使用/对过滤条件进行切分
    args = url_arg.split("/")
    # 测试过滤条件的长度
    len_arg = len(args)
    # 如果参数的个数是两个，那么安照参数1是类型 参数2是标签进行查询
    # 设置全局参数，防止在判断的时候有条件分支缺失导致变量不存在
    c_type = ""  # url传递过来的课程类型
    label = ""  # url传递过来的课程标签
    referer_url = ""  # 提供lable重新定位的参数
    referer_url1 = ""  # 提供给c_type重新定位的参数
    if len_arg == 2:  # 请求由类型也有标签
        c_type, label = args  # 分解参数
        # 查询python所有免费或者付费
        referer_url = "/courses/index/%s/" % c_type  # 定义lable标签的链接
        referer_url1 = label + "/"  # 定义课程类型的链接
        label_id = Label.query.filter_by(l_name=label)[0].id  # 获取对应的标签
        course_list = Course.query.filter(
            and_(
                Course.c_type == int(c_type),
                Course.label_id == label_id
            )
        )  # 查询所对应的多有课程
        if int(c_type) == 3:
            course_list = Course.query.filter(
                and_(
                    Course.label_id == label_id
                )
            )  # 查询所对应的多有课程

    # url只有一个路由请求参数
    elif len_arg == 1:
        arg, = args  # 获取参数
        if arg.isdigit():  # 通过类型判断参数是c_type 函数 lable
            c_type = arg  # 请求参数是c_type
            referer_url = "/courses/index/%s/" % c_type  # 定义lable标签的链接
            if int(c_type) == 3:  # 判断全部
                course_list = Course.query.all()
            else:
                course_list = Course.query.filter_by(c_type=int(c_type))
        else:
            label = arg
            referer_url1 = label + "/"  # 定义c_type标签的链接
            course_list = Label.query.filter_by(l_name=label)[0].c_label
    print("c_type: %s" % c_type)
    print("label: %s" % label)
    return render_template("courses/index.html", **locals())


@lou_app.route("/developer/index/")
def developer_index():
    return render_template("developer/index.html", **locals())


@lou_app.route("/paths/index/")
def paths_index():
    return render_template("paths/index.html", **locals())


@lou_app.route("/paths/show/")
def paths_show():
    return render_template("paths/show.html", **locals())


@lou_app.route("/questions/index/")
def questions_index():
    return render_template("questions/index.html", **locals())

@lou_app.route("/questions/show/")
def questions_show():
    return render_template("questions/show.html", **locals())


@lou_app.route("/bootcamp/index/")
def bootcamp_index():
    return render_template("bootcamp/index.html", **locals())


@lou_app.route("/user/13/questions/")
def user13_questions():
    return render_template("user/13/questions.html", **locals())


@lou_app.route("/user/13/reports/")
def user13_reports():
    return render_template("user/13/reports.html", **locals())


@lou_app.route("/user/13/reports_show/")
def user13_reports_show():
    return render_template("user/13/reports_show.html", **locals())


@lou_app.route("/user/13/study/")
def user13_study():
    return render_template("user/13/study.html", **locals())


@lou_app.route("/vip/index/")
def vip_index():
    return render_template("vip/index.html", **locals())


@lou_app.route("/privacy/index/")
def privacy_index():
    return render_template("privacy/index.html", **locals())


@lou_app.route("/labs/index/")
def labs_index():
    return render_template("labs/index.html", **locals())


@lou_app.route("/edu/index/")
def edu_index():
    return render_template("edu/index.html", **locals())


@lou_app.route("/courses/reports/")
def courses_reports():
    return render_template("courses/reports.html", **locals())


@lou_app.route("/courses/show/")
def courses_show():
    return render_template("courses/show.html", **locals())


@lou_app.route("/courses/show2/")
def courses_show2():
    return render_template("courses/show2.html", **locals())


@lou_app.route("/edu/uestc/")
def edu_uestc():
    return render_template("edu/uestc.html", **locals())


@lou_app.route("/al/")
def add_label():
    string = "Python C/C++ Linux Web 信息安全 PHP Java NodeJS Android " \
             "GO Spark 计算机专业课 Hadoop HTML5 Scala Ruby R 网络 " \
             "Git SQL NoSQL 算法 Docker Swift 汇编 Windows UI CAD"
    # string = ""
    for i in string.split():
        l = Label()
        l.l_name = i
        l.description = "%s课啊，真滴好啊"%i
        l.save()
    return "hello world"

#往数据库添加数据
@lou_app.route("/ac/")
def add_course():
    result = [
     {'src': 'https://dn-simplecloud.shiyanlou.com/ncn63.jpg', 'alt': '新手指南之玩转实验楼'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/ncn1.jpg', 'alt': 'Linux 基础入门（新版）'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1480389303324.png', 'alt': 'Kali 渗透测试 - 后门技术实战（10个实验）'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1480389165511.png', 'alt': 'Kali 渗透测试 - Web 应用攻击实战'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482113947345.png', 'alt': '使用OpenCV进行图片平滑处理打造模糊效果'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482807365470.png', 'alt': '使用 Python 解数学方程'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482215587606.png', 'alt': '跟我一起来玩转Makefile'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1480386391850.png', 'alt': 'Kali 渗透测试 - 服务器攻击实战（20个实验）'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482113981000.png', 'alt': '手把手教你实现 Google 拓展插件'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482113522578.png', 'alt': 'DVWA之暴力破解攻击'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1482113485097.png', 'alt': 'Python3实现简单的FTP认证服务器'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1481689616072.png', 'alt': 'SQLAlchemy 基础教程'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1481511769551.png', 'alt': '使用OpenCV&&C++进行模板匹配'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1481512189119.png', 'alt': 'Metasploit实现木马生成、捆绑及免杀'},
     {'src': 'https://dn-simplecloud.shiyanlou.com/1480644410422.png', 'alt': 'Python 3 实现 Markdown 解析器'}]
    for i in range(25):
        for cou in result:
            c = Course()
            name = cou.get("alt")
            if i != 0:
                name +=" (%s)"%i
            c.c_name = name  # 课程名称
            c.description = "%s课程啊，真滴好啊"%name  # 课程描述
            c.picture = cou.get("src")  # 课程logo
            c.show_number = random.randint(1,100000)  # 观看人数
            c.c_time_number = random.randint(7,32)  # 课时
            c.class_label = random.choice(Label.query.all())
            c.save()
    return "hello world"

#根据类型添加自定义数据
@lou_app.route("/get_test/", methods=["GET","POST"])
def get_test():
    course = ""
    label_list = Label.query.all()
    # for label in label_list:
    #     print(label.l_name)
    if request.method == "POST":
        data = request.form
        c_name = data.get("c_name")
        show_number = data.get("show_number")
        c_time_number = data.get("c_time_number")
        label = data.get("label")
        description = data.get("description")
        logo = request.files.get("logo")

        #保存文件分为两步
        # 文件保存到服务器
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "static\img\%s" % logo.filename
        )
        logo.save(file_path)
        #文件路径保存到数据中
        course = Course()
        course.c_name = c_name
        course.show_number = show_number
        course.description = description
        course.c_time_number = c_time_number
        course.picture = "/static\img\%s" % logo.filename #保存图片路径
        course.class_label = Label.query.get(int(label)) #保存外键
        course.save()

    return render_template("request_example.html", **locals())

#cookies请求
@lou_app.route("/cookies/")
def cookies():
    session["username"] = "laobian" #设置session
    session.get("username")  #获取session
    del session["username"]  #删除session
    return render_template("1.html")


@lou_app.route("/ajax/")
def ajax_example():
    return render_template("ajax_eample.html")


@lou_app.route("/ajax_user/",methods=["get","POST"])
def ajax_user():
    result = {"is_user":False}
    if request.method == "POST":
        nick_name = request.form.get("nick_name")
        email = request.form.get("email")
        password = request.form.get("password")
        user = User()
        user.nick_name = nick_name
        user.email = email
        user.password = set_password(password)
        user.save()
        result["is_user"] = True
    return result