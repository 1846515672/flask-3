from flask_wtf import FlaskForm
import wtforms
from wtforms import validators
from wtforms import ValidationError
from text.models import User

class OurError:
    def __init__(self, message=None):
        """
        :param message: 错误提示信息
        """
        self.message = message

    def __call__(self, form, field):
        """
        :param form: 固定参数,代表form表单<TestLou.form.UserForm object at 0x00000000046C6E80>
        :return: 固定参数  字段本身 <input id="username" name="username" type="text" value="bjh">
        """
        validata = field.data #字段数据 bjh
        db_user = User.query.filter_by(nick_name=validata).first()
        if db_user:
            self.message += ":用户名重复"
            raise ValidationError(self.message)
        pool = ["bjh"]
        if validata in pool:
            self.message += ":敏感词"
            raise ValidationError(self.message) #错误回收

class UserForm(FlaskForm):
    username = wtforms.SelectField("用户名", validators=[OurError("违法命名")])
    email = wtforms.SelectField("邮箱", validators=[validators.Email("邮箱格式错误!")])
    password = wtforms.PasswordField("密码")