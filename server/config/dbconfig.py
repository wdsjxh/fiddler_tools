import re


class dbconfig:
    mysqlhost = "127.0.0.1"
    mysqlport = 3306
    mysqluser = "root"
    mysqlpassword = ""
    mysqldbname = "fiddler_log"

    # my_api_path = "E:\\fiddler_tools\\client\\dist\\config.js"  # 后端接口对应文件路径，源码编译安装时需修改路径
    my_api_path = "/fiddler_tools/client/dist/config.js"  # 后端接口对应文件路径，源码编译安装时需修改路径
    my_api = "http://127.0.0.1"

    def getdbconfig(self):
        tempconfigdict = {}
        tempconfigdict["mysqlhost"] = self.mysqlhost
        tempconfigdict["mysqlport"] = self.mysqlport
        tempconfigdict["mysqluser"] = self.mysqluser
        tempconfigdict["mysqlpassword"] = self.mysqlpassword
        tempconfigdict["mysqldbname"] = self.mysqldbname
        return tempconfigdict

    def getmyapi(self):
        try:
            with open(file=self.my_api_path, mode='r', encoding='utf-8') as api_file:
                file_content = api_file.readlines()
                for line in file_content:
                    if "app_api_url" in line:
                        print(line)
                        pattern = re.compile("'(.*)'")
                        str_re1 = pattern.findall(line)
                        if str_re1:
                            return str_re1[0]
        except IOError as e:
            print(e)
            return self.my_api


# dbc = dbconfig()
# print(dbc.getmyapi())
