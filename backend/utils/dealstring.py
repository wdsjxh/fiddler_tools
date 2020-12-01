# stringfirst -large string
def is_only_onestring(stringfirst, stringsecond):
    if str(stringfirst).count(str(stringsecond)) == 1:
        return True
    else:
        return False

