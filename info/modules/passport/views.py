from flask import request
from flask import current_app
from flask import abort
from flask import make_response

from info import redis_store
from info import constants
from info.utils.captcha.captcha import captcha
from . import passport_blu


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