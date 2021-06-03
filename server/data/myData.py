class myData:
    cookie_first = "st_pvi=89905859672135"
    cookie_second = "second"

    spcookie = "my_token"  # 特殊token字段  需要自定义

    origin_userid = "277348"
    userid_first = "587722"
    userid_second = "44670"

    def get_cookie_first(self):
        return self.cookie_first

    def set_cookie_first(self, cookie_first):
        self.cookie_first = cookie_first

    def get_cookie_second(self):
        return self.cookie_second

    def set_cookie_second(self, cookie_second):
        self.cookie_second = cookie_second

    def get_origin_userid(self):
        return self.origin_userid

    def set_origin_userid(self, origin_userid):
        self.origin_userid = origin_userid

    def get_userid_first(self):
        return self.userid_first

    def set_userid_first(self, userid_first):
        self.userid_first = userid_first

    def get_userid_second(self):
        return self.userid_first

    def set_userid_second(self, userid_second):
        self.userid_second = userid_second
