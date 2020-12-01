import chardet


# 返回编码
def returnwebsitecharset(responsecontent):
    codesty = chardet.detect(responsecontent)
    tempcode = codesty['encoding']
    print(tempcode)
    print(type(tempcode))
    if tempcode:
        return tempcode
    else:
        return None


# checkwebsitecharset
# GB2312 报错
def checkwebsitecharset(responsecontent):
    if responsecontent is None:
        return None
    codesty = chardet.detect(responsecontent)
    tempcode = codesty['encoding']
    print(tempcode)
    print(type(tempcode))
    if tempcode == "GB2312":
        tempcode = "gb18030"
    try:
        decodedcontent = responsecontent.decode(tempcode)
        return decodedcontent
    except Exception as e:
        print(e)
        if tempcode is None:
            print("探测编码为None")
            print(responsecontent)
            try:
                decodedcontent = responsecontent.decode("utf-8")
                return decodedcontent
            except Exception as e:
                print(e)
                print("依然异常")
                return None
        else:
            return None

    # return responsecontent.decode(codesty['encoding'])
