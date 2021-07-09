__author__ = 'Harutya'
__date__ = '2021/07/09'


def response(code, message, data):
    return dict(code=code, message=message, data=data)


def success(data):
    return response('200', 'succeed!', data)


def error(data):
    return response('500', 'error!', data)
