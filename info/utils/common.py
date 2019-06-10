def do_index_class(index):
    """
    Custom filter used to html_class sort
    :param index:
    :return:
    """
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''
