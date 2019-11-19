from flask import redirect
from flask import Response
import  hashlib
import  functools
from flask import request

def LoginValid(fun):
    @functools.wraps(fun)
    def inner(*args, **kwargs):
        username = request.cookies.get("email")
        if username:
            return fun(*args, **kwargs)
        else:
            return redirect("/courses/index/3/")

    return inner