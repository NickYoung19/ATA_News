import random
import re
from datetime import datetime

from flask import request, session
from flask import current_app
from flask import abort
from flask import make_response
from flask import jsonify

from info import redis_store, db
from info import constants
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.modules.passport import passport_blu
from info.utils.response_code import RET


@passport_blu.route('/image_code')
def get_image_code():
    """
    Generate a image code and return
    :return:
    """
    # Get url params with request.args method
    image_code_id = request.args.get('imageCodeId', None)
    if not image_code_id:
        return abort(404)
    # Generate a image code
    name, text, image = captcha.generate_captcha()
    try:
        # Save image code to redis
        redis_store.set('imageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        current_app.logger.debug('生成的图片验证码为: %s' % text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # Return image code to browser
    response = make_response(image)
    # Set response header data type
    response.headers['Content-Type'] = 'image/jpg'
    return response


@passport_blu.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    Realized send sms code
    :return:
    """
    # Get json to dict with request json method
    params_dict = request.json
    print('用户请求的参数: %s' % params_dict)
    # Get params from front-end
    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id = params_dict.get('image_code_id')

    # Judge params integrality
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # Judge mobile format
    if not re.match(r'1[356789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        # Get image code from redis
        real_image_code = redis_store.get('imageCodeId_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # User input image_code compare to real_image_code
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # Generate sms_code
    sms_code_str = '%06d' % random.randint(0, 999999)
    current_app.logger.debug("生成的短信验证码是: %s" % sms_code_str)

    # Send sms_code
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 300], 1)

    # Save sms_code to redis
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信失败')

    try:
        redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据保存失败')

        # 返回发送结果
    return jsonify(errno=RET.OK, errmsg='发送成功')


@passport_blu.route('/register', methods=['POST'])
def register():
    """
    Realized register function
    :return:
    """
    # Receive parameters passed by the front end
    params_dict = request.json
    mobile = params_dict.get('mobile')
    smscode = params_dict.get('smscode')
    password = params_dict.get('password')

    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match(r'1[356789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        # Get sms code from redis
        real_sms_code = redis_store.get('SMS_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # Add the correct data to the mysql database
    user = User()
    user.nick_name = mobile
    # user.password_hash = password
    user.password = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # Save user login status
    session['user_id'] = user.id
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/login', methods=['POST'])
def login():
    """
    Realized user login function
    :return:
    """
    # Receive parameters passed by the front end
    params_dict = request.json
    mobile = params_dict.get('mobile')
    passport = params_dict.get('passport')

    # Calibration receive params from front end
    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not re.match(r'1[356789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户没有注册")

    # Calibration user input's password
    if not user.check_passowrd(passport):
        return jsonify(errno=RET.PWDERR, errmsg="密码输入错误")

    # Set user last login datetime
    user.last_login = datetime.now()

    # Save user login status
    session['user_id'] = user.id

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="登录成功")
