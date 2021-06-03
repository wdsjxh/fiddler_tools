from html import unescape


# 对比payload是否在返回包
def dealstringencode(htmlstring, tocomparestring):
    if tocomparestring in htmlstring:
        return True
    elif tocomparestring in unescape(htmlstring):
        return True
    else:
        return False


# if dealstringencode("fsadfgsdff&#39alert(xss)", "'alert(xss)"):
#     print("fsdf")
