import random
import re

from flask import request
from flask import current_app
from flask import abort
from flask import make_response
from flask import jsonify

from info import redis_store
from info import constants
from info.libs.yuntongxun.sms import CCP
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
    current_app.logger.debug(sms_code_str)

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
