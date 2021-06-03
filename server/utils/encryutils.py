import hashlib
import uuid
import time


class encryutils():
    # user pass salt
    def passwordenc(self, password, salt):
        salt = salt.encode("utf-8")
        m = hashlib.md5(salt)
        m.update(password.encode("utf-8"))

        md5_value = m.hexdigest()
        return md5_value

    # salt uuid
    def newsalt(self):
        uid = str(uuid.uuid4())
        suid = ''.join(uid.split('-'))
        return suid

    # 生成token
    def newtoken(self, username, salt_laststring):
        time_tup = time.time()
        timestamp = str(int(time_tup))
        tokenstring = username + salt_laststring + timestamp
        salt = salt_laststring.encode("utf-8")
        m = hashlib.md5(salt)
        m.update(tokenstring.encode("utf-8"))

        md5_value = m.hexdigest()
        return md5_value

    # 生成抓包token username + token[-5:-11] + timstamp[-5:]
    def new_capture_token(self, username, token):
        time_tup = time.time()
        timestamp = str(int(time_tup))[-5:]
        tokenstring = username + str(token)[-5:-11] + timestamp
        salt = token.encode("utf-8")
        m = hashlib.md5(salt)
        m.update(tokenstring.encode("utf-8"))

        md5_value = m.hexdigest()
        return md5_value

# my_encry = encryutils()
# print(my_encry.passwordenc("admin", ""))
