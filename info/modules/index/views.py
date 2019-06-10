from flask import render_template, session
from flask import current_app

from info import redis_store, constants
from info.models import User, News, Category
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

    # Function: If user logined and add user_info to current user home page
    # Get the user_id from cookie
    user_id = session.get('user_id')
    user = None
    if user_id:
        try:
            # Search user_id on mysql
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # Function: Realizes news ranking at the right
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # news_list: [obj, obj, obj]   --->   [{}, {}, {}]
    news_dict_li = [news.to_basic_dict() for news in news_list]

    # Function: Show news category at home page
    categories = []
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # categories: [obj, obj, obj]   --->   [{}, {}, {}]
    category_li = [category.to_dict() for category in categories]

    # Add rendering data
    data = {
        # Change user_obj to dict format
        "user_info": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "category_li": category_li
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