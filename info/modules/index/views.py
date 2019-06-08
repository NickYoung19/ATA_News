from flask import render_template
from flask import current_app

from info import redis_store
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
    return render_template('news/index.html')


@index_blu.route('/favicon.ico')
def favicon():
    """
    Add a ICONS to the site
    :return:
    """
    return current_app.send_static_file('news/favicon.ico')