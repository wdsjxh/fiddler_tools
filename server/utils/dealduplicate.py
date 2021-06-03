import hashlib


# 判断重复数据包，MD5值
class dealduplicate:
    md5list = []

    def dealduplicatemain(self, requeststring):
        requeststringmd5 = self.getStrAsMD5(requeststring)
        print(requeststringmd5)
        if requeststringmd5 in self.md5list:
            return True
        else:
            self.md5list.append(requeststringmd5)
            return False

    def getStrAsMD5(self, parmStr):
        # 1、参数必须是utf8
        # 2、python3所有字符都是unicode形式，已经不存在unicode关键字
        # 3、python3 str 实质上就是unicode
        if isinstance(parmStr, str):
            # 如果是unicode先转utf-8
            parmStr = parmStr.encode("utf-8")
        m = hashlib.md5()
        m.update(parmStr)
        return m.hexdigest()

# dealexp = dealduplicate()
# if dealexp.dealduplicatemain("fsdfsdf"):
#     print("重复")
# else:
#     print("没有重复")
#
# if dealexp.dealduplicatemain("fsdfsdf2"):
#     print("重复")
# else:
#     print("没有重复")
#
# if dealexp.dealduplicatemain("fsdfsdf"):
#     print("重复")
# else:
#     print("没有重复")
