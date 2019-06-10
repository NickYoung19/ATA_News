from flask import render_template, session
from flask import current_app

from info import redis_store
from info.models import User
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    """
    Home page rendering
    :return:
    """
    # It proves that the session has been integrated already
    # redis_store.session = ['name', 'miaomiao']
    # return 'Success into Blueprint'

    # if user logined and add user_info to current user home page
    # Get the user_id from cookie
    user_id = session.get('user_id')
    user = None
    if user_id:
        try:
            # Search user_id on mysql
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        # Change user_obj to dict format
        "user_info": user.to_dict() if user else None
    }

    # Rendering data to home page
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    """
    Add a ICONS to the site
    :return:
    """
    return current_app.send_static_file('news/favicon.ico')