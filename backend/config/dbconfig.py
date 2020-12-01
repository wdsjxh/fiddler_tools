class dbconfig:
    mysqlhost = "127.0.0.1"
    mysqlport = 3306
    mysqluser = "root"
    mysqlpassword = ""
    mysqldbname = "fiddler_log"

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
        return self.my_api

# dbc = dbconfig()
# print(dbc.getmyapi())
