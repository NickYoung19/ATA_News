from flask import render_template
from flask import current_app
from flask import session
from flask import request
from flask import jsonify

from info import redis_store, constants
from info.models import User, News, Category
from info.modules.index import index_blu
from info.utils.response_code import RET


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


@index_blu.route('/news_list')
def news_list():
    """
    Realizes home page news list
    :return:
    """
    cid = request.args.get('cid')
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10) # default: 10/page

    # Calibration data
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # Search data by mysql
    filters = []
    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)
