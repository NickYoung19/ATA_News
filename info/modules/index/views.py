from info import redis_store
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    # It proves that the session has been integrated already
    redis_store.session = ['name', 'miaomiao']
    return 'Success into Blueprint'
