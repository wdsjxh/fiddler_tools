excptlist = ["nested exception is java.lang.NumberFormatException:",
             "no String-argument constructor/factory method to deserialize from String value",
             "java.lang.NumberFormatException:",
             "JSON parse error"]

excptlistoutofaccess = ["登录失败", "权限无效", "会话超时", "访问被拒绝", "非登录用户", "没有权限", "Authentication failure",
                        "0001-01-01T00:00:00", "用户名或密码错误", "重新登录", "登录验证失败", "验证用户信息失败", "调用接口错误"]


class dealexpvul:
    def dealexpvulmain(self, respdecoded):
        print("deal")
        for excptline in excptlist:
            if excptline in respdecoded:
                return True
        # if "no String-argument constructor/factory method to deserialize from String value" in respdecoded:
        #     return True

    # 越权误报 排除  {"body":{"resultMsg":"非登录用户，访问被拒绝。","retValue":-403}}
    def dealexpoutofaccess(self, respcontent):
        print("deal")
        for excptline in excptlistoutofaccess:
            if excptline in respcontent:
                return True

# dealexp = dealexpvul()
# if dealexp.dealexpvulmain("{\"success\":false,\"info\":\"权限无效，请先去重新登录，以获取权限！\",\"data\":-1,\"totalPageCount\":-1,\"errorCode\":\"UANDCTOKEN_INVALID\",\"totalRecordsCount\":-1}"):
#     print("ok")
# else:
#     print("正确")
