import json
import datetime
import copy
import pymysql
from utils.timeutils import datetime_compare
from utils.timeutils import datetime_add8
from utils.timeutils import make_year_month_dict
from config.dbconfig import dbconfig
from utils.encryutils import encryutils


class mysqlutil:
    mydbconfig = dbconfig()
    myencryutils = encryutils()

    def __init__(self):
        self.sqldata = []
        self.resultlist = []

    # 抓包处获取过滤配置
    def get_config(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT content,type FROM config; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT content,type FROM config WHERE " + sqlquerystring
            print(sql)

            cur.execute(sql, sqldata)
        resultdict = {}

        u = cur.fetchall()
        for u_line in u:
            resultdict[u_line[0]] = u_line[1]
        cur.close()
        conn.close()
        return resultdict

    # 抓包入库   customers  exp
    def add_packet(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()

        data = {
            'id': requestdict["id"],
            'time': requestdict["time"],
            'request': requestdict["request"],
            'response': requestdict["response"],
            'method': requestdict["method"],
            'httptype': requestdict["httptype"],
            'project': requestdict["project"],
            'username': requestdict["username"],
        }

        table_name = 'customers'
        # # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
        keys = ', '.join(data.keys())
        #
        values = ', '.join(['%s'] * len(data))
        #
        sql = 'REPLACE  INTO {table}({keys}) VALUES ({values})'.format(table=table_name, keys=keys, values=values)

        try:
            # 这里的第二个参数传入的要是一个元组
            if cur.execute(sql, tuple(data.values())):
                print('add scan  ' + str(table_name) + ' Successful')
                conn.commit()
            else:
                print('add scan ' + str(table_name) + ' None')
        except Exception as e:
            print('Failed')
            print(e)
            conn.rollback()

        cur.close()
        conn.close()
        if requestdict["add_flag"] == "exp":
            self.add_packet_exp(requestdict)

    # 抓包入库   customers  exp
    def add_packet_exp(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()

        data = {
            'id': requestdict["id"],
            'time': requestdict["time"],
            'request': requestdict["request"],
            'response': requestdict["response"],
            'method': requestdict["method"],
            'httptype': requestdict["httptype"],
            'project': requestdict["project"],
            'username': requestdict["username"],
        }

        exp_table_name = 'customers_exp'
        # # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
        keys = ', '.join(data.keys())
        #
        values = ', '.join(['%s'] * len(data))
        #
        sql = 'REPLACE  INTO {table}({keys}) VALUES ({values})'.format(table=exp_table_name, keys=keys, values=values)

        try:
            # 这里的第二个参数传入的要是一个元组
            if cur.execute(sql, tuple(data.values())):
                print('add scan  ' + str(exp_table_name) + ' Successful')

                conn.commit()
            else:
                print('add scan ' + str(exp_table_name) + ' None')
        except Exception as e:
            print('Failed')
            print(e)
            conn.rollback()

        cur.close()
        conn.close()

    def uninit(self):  # 重新初始化
        self.sqldata = []

    def get_conn(self):
        conn = pymysql.connect(host=self.mydbconfig.getdbconfig()["mysqlhost"],
                               user=self.mydbconfig.getdbconfig()["mysqluser"],
                               password=self.mydbconfig.getdbconfig()["mysqlpassword"],
                               db=self.mydbconfig.getdbconfig()["mysqldbname"],
                               port=self.mydbconfig.getdbconfig()["mysqlport"],
                               charset='utf8'
                               )
        return conn

    def write_vulnerability_to_db(self, requestdict, total_type, details_type, insert_flag, my_id, my_time,
                                  request_data, origin_response,
                                  my_method, result):
        conn = self.get_conn()
        cur = conn.cursor()
        try:
            if isinstance(origin_response, str):
                responsedata = origin_response
            else:
                responsedata = str(origin_response.decode())
        except Exception as e:
            print(e)
            responsedata = "编码错误"

        data = {
            'id': my_id,
            'time': my_time,
            'request': request_data,
            'response': responsedata,
            'method': my_method,
            'total_type': total_type,
            'details_type': details_type,
            'details': result,
        }
        data.update(requestdict)  # 添加username project
        table_name = 'vulnerable'
        # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
        keys = ', '.join(data.keys())

        values = ', '.join(['%s'] * len(data))

        sql = 'REPLACE  INTO {table}({keys}) VALUES ({values})'.format(table=table_name, keys=keys, values=values)
        try:
            # 这里的第二个参数传入的要是一个元组
            if cur.execute(sql, tuple(data.values())):
                print('Successful')
                if insert_flag == "xss":  # xss平台数据更新
                    print("xss_flag")
                    # TODO邮件告警等
                conn.commit()
            else:
                if insert_flag == "xss":  # xss平台数据更新,重复的
                    print("xss exist")

        except Exception as e:
            print('Failed')
            print(e)
            conn.rollback()
        cur.close()
        conn.close()

    def user_config_mul(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                if keyline == "valid" and valueline == "启用":
                    valueline = 1
                elif keyline == "valid" and valueline == "禁用":
                    valueline = 0
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT myuser,roles,valid,validtime FROM user ; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT myuser,roles,valid,validtime FROM user WHERE " + sqlquerystring
            print(sql)

            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["username"] = u_line[0]
            tempdict["roles"] = u_line[1]
            if u_line[2] == 1:
                tempdict["valid"] = "启用"
            else:
                tempdict["valid"] = "禁用"
            tempdict["validtime"] = str(u_line[3])
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    def user_config_mullimit(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        pagestring = ""
        limitstring = ""

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":
                if keyline == "limit":
                    limitstring = int(valueline)
                    print(limitstring)
                elif keyline == "page":
                    pagestring = int(valueline)
                    print(pagestring)
                elif keyline == "valid" and valueline == "启用":
                    valueline = 1
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
                elif keyline == "valid" and valueline == "禁用":
                    valueline = 0
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
                else:  # 判断每一个条件内容
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)

        print(sqlquery)
        startno = (int(pagestring) - 1) * int(limitstring)
        stopno = limitstring
        limitquerystring = " limit  %s, %s  ;"
        print(limitquerystring)
        sqldata.append(startno)
        sqldata.append(stopno)
        print("测试valid字段")
        print(sqldata)
        if not sqlquery:
            sql = "SELECT myuser,roles,valid,validtime FROM user  " + limitquerystring
            # cur.execute(sql, sqldata)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)

            # 加上类型 方法
            sql = "SELECT myuser,roles,valid,validtime FROM user WHERE " + sqlquerystring + limitquerystring

        print("sql语句")
        print(sql)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["username"] = u_line[0]
            tempdict["roles"] = u_line[1]
            if u_line[2] == 1:
                tempdict["valid"] = "启用"
            else:
                tempdict["valid"] = "禁用"
            tempdict["validtime"] = str(u_line[3])
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 项目界面多条件搜索功能
    def project_config_mul(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT id,content,type,time,config_name FROM project_config; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT id,content,type,time,config_name FROM project_config WHERE " + sqlquerystring
            print(sql)

            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["content"] = u_line[1]
            tempdict["type"] = u_line[2]
            tempdict["time"] = str(u_line[3])
            if str(u_line[4]) and u_line[4] is not None:
                tempdict["config_name"] = str(u_line[4])
            else:
                tempdict["config_name"] = "配置为空"
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 配置界面多条件搜索功能limit
    def project_config_mullimit(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        pagestring = ""
        limitstring = ""

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":
                if keyline == "limit":
                    limitstring = int(valueline)
                    print(limitstring)
                elif keyline == "page":
                    pagestring = int(valueline)
                    print(pagestring)
                else:  # 判断每一个条件内容
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)

        print(sqlquery)
        startno = (int(pagestring) - 1) * int(limitstring)
        stopno = limitstring
        limitquerystring = " limit  %s, %s  ;"
        print(limitquerystring)
        sqldata.append(startno)
        sqldata.append(stopno)
        print(sqldata)
        if not sqlquery:
            sql = "SELECT id,content,type,time,config_name FROM project_config  " + limitquerystring
            # cur.execute(sql, sqldata)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)

            # 加上类型 方法
            sql = "SELECT id,content,type,time,config_name FROM project_config WHERE " + sqlquerystring + limitquerystring

        print("sql语句")
        print(sql)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["content"] = u_line[1]
            tempdict["type"] = u_line[2]
            tempdict["time"] = str(u_line[3])
            if str(u_line[4]) and u_line[4] is not None:
                tempdict["config_name"] = str(u_line[4])
            else:
                tempdict["config_name"] = "配置为空"
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 数据包界面多条件搜索功能
    def vulnerable_config_mul(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT id,content,type FROM config; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT id,content,type FROM config WHERE " + sqlquerystring
            print(sql)

            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["content"] = u_line[1]
            tempdict["type"] = u_line[2]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 配置界面多条件搜索功能limit
    def vulnerable_config_mullimit(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        pagestring = ""
        limitstring = ""

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":
                if keyline == "limit":
                    limitstring = int(valueline)
                    print(limitstring)
                elif keyline == "page":
                    pagestring = int(valueline)
                    print(pagestring)
                else:  # 判断每一个条件内容
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)

        print(sqlquery)
        startno = (int(pagestring) - 1) * int(limitstring)
        stopno = limitstring
        limitquerystring = " limit  %s, %s  ;"
        print(limitquerystring)
        sqldata.append(startno)
        sqldata.append(stopno)
        print(sqldata)
        if not sqlquery:
            sql = "SELECT id,content,type FROM config  " + limitquerystring
            # cur.execute(sql, sqldata)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)

            # 加上类型 方法
            sql = "SELECT id,content,type FROM config WHERE " + sqlquerystring + limitquerystring

        print("sql语句")
        print(sql)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["content"] = u_line[1]
            tempdict["type"] = u_line[2]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 数据包排除请求包数据 返回列表
    def get_request_customers_exp(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT request FROM customers_exp; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT request FROM customers_exp WHERE " + sqlquerystring
            print(sql)
            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            resultlist.append(u_line[0])
        cur.close()
        conn.commit()
        conn.close()
        return resultlist

    # 主数据包大部分数据 返回字典列表
    def get_most_customers(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT id,time,request,method,httptype FROM customers; "
            print(sql)
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT id,time,request,response,method,httptype FROM customers WHERE " + sqlquerystring
            print(sql)
            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["httptype"] = u_line[5]
            resultlist.append(tempdict)
        cur.close()
        conn.commit()
        conn.close()
        return resultlist

    # 数据包界面多条件搜索功能
    def data_packet_mul(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        starttimeflag = False
        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    print("需要时间判断")
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        print(sqlquery)
        if not sqlquery:
            sql = "SELECT * FROM customers; "
            print(sql)
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)
            # 加上类型 方法
            sql = "SELECT * FROM customers WHERE " + sqlquerystring
            print(sql)

            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if starttimeflag:
                if not datetime_compare(u_line[1], requestdict['starttime'], requestdict['stoptime']):
                    continue
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["type"] = u_line[5]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 数据包界面多条件搜索功能limit
    def data_packet_mullimit(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        pagestring = ""
        limitstring = ""
        starttimeflag = False
        for keyline, valueline in dict(requestdict).items():
            print(keyline)
            if valueline != "0":
                if keyline == "limit":
                    limitstring = int(valueline)
                    print(limitstring)
                elif keyline == "page":
                    pagestring = int(valueline)
                    print(pagestring)
                elif keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    print("需要时间判断")
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:  # 判断每一个条件内容
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)

        print(sqlquery)
        startno = (int(pagestring) - 1) * int(limitstring)
        stopno = limitstring
        limitquerystring = " limit  %s, %s  ;"
        print(limitquerystring)
        sqldata.append(startno)
        sqldata.append(stopno)
        print(sqldata)
        if not sqlquery:
            sql = "SELECT * FROM customers  " + limitquerystring
            # cur.execute(sql, sqldata)
        else:
            sqlquerystring = " and ".join(sqlquery)
            print(sqlquerystring)
            print(sqldata)

            # 加上类型 方法
            sql = "SELECT * FROM customers WHERE " + sqlquerystring + limitquerystring

        print("sql语句")
        print(sql)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if starttimeflag:
                if not datetime_compare(u_line[1], requestdict['starttime'], requestdict['stoptime']):
                    continue
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["type"] = u_line[5]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 数据包界面搜索功能
    def data_packet_search(self, method):
        conn = self.get_conn()
        cur = conn.cursor()
        # 加上类型 方法
        sql = "SELECT * FROM customers WHERE method = %s"

        method = (method,)

        cur.execute(sql, method)

        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["type"] = u_line[5]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # group by
    def vulnerable_details_group_by_method(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        print(requestdict)

        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                if keyline == "value":
                    continue
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT DISTINCT method FROM vulnerable; "
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT DISTINCT method  FROM vulnerable WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        print(sql)
        conn.commit()
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            my_method = u_line[0]
            if my_method not in resultlist:
                resultlist.append(my_method)
        cur.close()
        conn.close()
        return resultlist

    # group by
    def vulnerable_details_group_by_total_type(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                if keyline == "value":
                    continue
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT DISTINCT total_type FROM vulnerable; "
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT DISTINCT total_type  FROM vulnerable WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        conn.commit()
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            my_method = u_line[0]
            if my_method not in resultlist:
                resultlist.append(my_method)
        cur.close()
        conn.close()
        return resultlist

    # group by
    def vulnerable_details_group_by_details_type(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []

        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                if keyline == "value":
                    continue
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT DISTINCT details_type FROM vulnerable; "
            cur.execute(sql)
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT DISTINCT details_type  FROM vulnerable WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        conn.commit()
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            my_method = u_line[0]
            if my_method not in resultlist:
                resultlist.append(my_method)
        cur.close()
        conn.close()
        return resultlist

    # 数据包界面多条件搜索功能
    def vulnerable_details_mul(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        starttimeflag = False
        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT id,time,request,response,method,details FROM vulnerable; "
            print(sql)
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT id,time,request,response,method,details  FROM vulnerable WHERE " + sqlquerystring
            cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if starttimeflag:
                if not datetime_compare(u_line[1], requestdict['starttime'], requestdict['stoptime']):
                    continue
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["details"] = u_line[5]
            # tempdict["total_type"] = u_line[6]
            # tempdict["details_type"] = u_line[7]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 数据包界面多条件搜索功能limit
    def vulnerable_details_mullimit(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        pagestring = ""
        limitstring = ""
        starttimeflag = False
        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":
                if keyline == "limit":
                    limitstring = int(valueline)
                elif keyline == "page":
                    pagestring = int(valueline)
                elif keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:  # 判断每一个条件内容
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)

        startno = (int(pagestring) - 1) * int(limitstring)
        stopno = limitstring
        limitquerystring = " limit  %s, %s  ;"
        sqldata.append(startno)
        sqldata.append(stopno)
        if not sqlquery:
            sql = "SELECT id,time,request,response,method,details FROM vulnerable  " + limitquerystring
        else:
            sqlquerystring = " and ".join(sqlquery)

            # 加上类型 方法
            sql = "SELECT id,time,request,response,method,details FROM vulnerable WHERE " + sqlquerystring + limitquerystring
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if starttimeflag:
                if not datetime_compare(u_line[1], requestdict['starttime'], requestdict['stoptime']):
                    continue
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["time"] = u_line[1]
            tempdict["request"] = u_line[2]
            tempdict["response"] = u_line[3]
            tempdict["method"] = u_line[4]
            tempdict["details"] = u_line[5]
            # tempdict["total_type"] = u_line[6]
            # tempdict["details_type"] = u_line[7]
            if tempdict not in resultlist:
                resultlist.append(tempdict)
        conn.close()
        return resultlist

    # 配置界面删除功能
    def config_delete_id(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "DELETE FROM config WHERE id = %s and username = %s ;"
        print(requestdict["deleteid"])
        print(sql)
        deletedata = int(requestdict["deleteid"])
        print(type(deletedata))
        print(deletedata)
        sqldata.append(deletedata)
        sqldata.append(requestdict["username"])
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 项目配置界面删除功能
    def project_config_delete_id(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "DELETE FROM project_config WHERE id = %s and username = %s ;"
        print(sql)
        deletedata = int(requestdict["deleteid"])
        sqldata.append(deletedata)
        sqldata.append(requestdict["username"])
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def project_config_bind(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "UPDATE  project_config SET config_name = %s WHERE id = %s"
        print(sql)
        mydict = json.loads(requestdict["bind_config"])
        print(mydict)
        sqldata.append(mydict["content"])
        sqldata.append(mydict["id"])
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 配置界面编辑功能
    def config_edit(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "UPDATE  config SET content = %s , type = %s  WHERE id = %s and username = %s;"
        mydict = json.loads(requestdict["edit"])
        sqldata.append(mydict["content"])
        sqldata.append(mydict["type"])
        sqldata.append(mydict["id"])
        sqldata.append(requestdict["username"])

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def dev_vulnerable_update(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "UPDATE  vulnerable SET total_type = %s , details_type = %s WHERE id = %s"
        sqldata.append(requestdict["total_type"])
        sqldata.append(requestdict["details_type"])
        sqldata.append(requestdict["id"])

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 项目配置界面编辑功能
    def project_col_edit(self, requestdict):
        print(requestdict)

        # 需要提前获取原来的项目名，方便其他表的项目名称修改
        # project  mydict["origin_content"]  mydict["content"]

        conn = self.get_conn()

        temp_sqldata = []
        temp_sqldata.append(requestdict["content"])
        temp_sqldata.append(requestdict["origin_content"])
        print(temp_sqldata)
        temp_cur = conn.cursor()

        sql = " UPDATE  customers  SET project  =  %s  WHERE project = %s ;"
        temp_cur.execute(sql, temp_sqldata)

        sql = " UPDATE  customers_exp  SET project  =  %s  WHERE project = %s ;"
        temp_cur.execute(sql, temp_sqldata)

        sql = " UPDATE  scan_config  SET project  =  %s  WHERE project = %s ;"
        temp_cur.execute(sql, temp_sqldata)

        sql = " UPDATE  vulnerable  SET project  =  %s  WHERE project = %s ;"
        temp_cur.execute(sql, temp_sqldata)

        conn.commit()
        temp_cur.close()

        conn.close()

    # 项目配置界面编辑功能
    def project_config_edit(self, requestdict):
        print(requestdict)
        mydict = json.loads(requestdict["edit"])

        tempdict = {}
        tempdict["origin_content"] = mydict["origin_content"]
        tempdict["content"] = mydict["content"]
        self.project_col_edit(tempdict)

        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "UPDATE  project_config SET content = %s , type = %s  WHERE id = %s ;"

        sqldata.append(mydict["content"])
        sqldata.append(mydict["type"])
        sqldata.append(mydict["id"])

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 配置界面添加功能
    def config_add(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "INSERT INTO  config  ( content , type ,username) VALUES  ( %s ,  %s , %s);"
        print(sql)

        mydict = json.loads(requestdict["add"])
        sqldata.append(mydict["content"])
        sqldata.append(mydict["type"])
        sqldata.append(requestdict["username"])
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 项目配置界面添加功能
    def project_add(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "INSERT INTO  project_config  ( content , type , time , valid , username, status) VALUES  ( %s,%s,%s,%s,%s,%s);"
        print(sql)

        mydict = json.loads(requestdict["add"])
        print(mydict)
        print(mydict["content"])
        print(mydict["type"])
        sqldata.append(mydict["content"])
        sqldata.append(mydict["type"])
        sqldata.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sqldata.append(1)
        sqldata.append(requestdict["username"])
        sqldata.append("stop")
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def adduser(self, username, password, roles):
        conn = self.get_conn()
        cur = conn.cursor()
        mysalt = self.myencryutils.newsalt()
        print(mysalt)
        sqldata = []
        mydict = {}
        insert_password = self.myencryutils.passwordenc(password, mysalt)
        try:
            sql = "INSERT  INTO  user  ( myuser , password ,salt ,roles ,valid ) VALUES  ( %s ,  %s , %s , %s , %s);"
            sqldata.append(username)
            sqldata.append(insert_password)
            sqldata.append(mysalt)
            sqldata.append(roles)
            sqldata.append(1)
            print(sqldata)
            cur.execute(sql, sqldata)
            mydict = {"code": 20000, "data": {"message": "注册成功"}}
        except Exception as e:
            print(e)
            mydict = {"code": 50043, "message": "用户已存在"}
        conn.commit()
        conn.close()
        return mydict

    def adduser_from_backend(self, mydict):
        conn = self.get_conn()
        cur = conn.cursor()
        mysalt = self.myencryutils.newsalt()
        print(mysalt)

        sqldata = []
        resultdict = {}
        insert_password = self.myencryutils.passwordenc(mydict["password"], mysalt)
        try:
            sql = "INSERT  INTO  user  ( myuser , password ,salt ,roles ,valid ) VALUES  ( %s ,  %s , %s , %s , %s);"
            sqldata.append(mydict["username"])
            sqldata.append(insert_password)
            sqldata.append(mysalt)
            sqldata.append(mydict["roles"])
            sqldata.append(int(mydict["status"]))
            print(sqldata)
            cur.execute(sql, sqldata)
            resultdict = {"code": 20000, "data": {"message": "后台添加用户成功"}}
        except Exception as e:
            print(e)
            resultdict = {"code": 50043, "message": "添加用户失败"}
        conn.commit()
        conn.close()
        return resultdict

    def user_config_edit(self, mydict):

        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "UPDATE  user SET roles = %s , valid = %s  WHERE myuser = %s ;"

        sqldata.append(mydict["roles"])
        sqldata.append(int(mydict["status"]))
        sqldata.append(mydict["username"])

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def user_config_delete_user(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "DELETE FROM user WHERE myuser = %s"
        print(sql)
        deletedata = str(requestdict["delete_user"])
        sqldata.append(deletedata)
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def add_segment(self, request_md5, request_data, id, request_json, response_json):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "INSERT ignore INTO  segment  ( request_md5 ,request_data, id ,request_json ,response_json) VALUES  ( %s , %s, %s , %s , %s);"
        sqldata.append(request_md5)
        sqldata.append(request_data)
        sqldata.append(id)
        print(type(request_json))
        sqldata.append(str(request_json))
        sqldata.append(str(response_json))

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def add_logineduser(self, logined_token, username):

        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "INSERT ignore INTO  logined  ( logined_token,username ) VALUES  ( %s ,  %s);"
        sqldata.append(logined_token)
        sqldata.append(username)
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # 获取用户表 username
    def get_userinfo(self, username):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "SELECT password,salt,introduction,roles,avatar,capture_token FROM user   where myuser = %s"
        sqldata.append(username)

        cur.execute(sql, sqldata)
        conn.commit()
        tempdict = {}
        u = cur.fetchall()
        for u_line in u:
            tempdict["password"] = u_line[0]
            tempdict["salt"] = u_line[1]
            if not u_line[2] or u_line[2] == "":
                tempdict["introduction"] = "个人介绍为空"
            else:
                tempdict["introduction"] = u_line[2]
            tempdict["roles"] = str(u_line[3]).split('ahahaha')
            if not u_line[4] or u_line[4] == "":
                tempdict["avatar"] = "https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif"
            else:
                tempdict["avatar"] = u_line[4]
            tempdict["capture_token"] = u_line[5]  # 抓包认证token
        conn.close()

        return tempdict

    def get_user_role(self, username):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "SELECT roles FROM user   where myuser = %s"
        sqldata.append(username)
        cur.execute(sql, sqldata)
        conn.commit()
        tempdict = {}
        u = cur.fetchall()
        for u_line in u:
            tempdict["roles"] = str(u_line[0])
        conn.close()
        return tempdict

    # 获取用户表 capture_token
    def get_userby_capture_token(self, capture_token):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "SELECT myuser,roles FROM user   where capture_token = %s"
        sqldata.append(capture_token)

        cur.execute(sql, sqldata)
        conn.commit()
        tempdict = {}
        u = cur.fetchall()
        for u_line in u:
            tempdict["username"] = u_line[0]
            tempdict["roles"] = u_line[1]
        conn.close()
        return tempdict

    # username  return project name list
    def get_projectname_by_username(self, username):
        conn = self.get_conn()
        cur = conn.cursor()
        sql = "SELECT content FROM project_config where username = %s GROUP BY time desc , id desc  ;"
        sqldata = []
        sqldata.append(username)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if u_line[0] not in resultlist:
                resultlist.append(u_line[0])
        conn.close()
        return resultlist

    def get_configname_by_username(self, username):
        conn = self.get_conn()
        cur = conn.cursor()
        sql = "SELECT config_name FROM scan_config where username = %s GROUP BY config_name ;"
        sqldata = []
        sqldata.append(username)
        cur.execute(sql, sqldata)
        resultlist = []

        u = cur.fetchall()
        for u_line in u:
            if u_line[0] not in resultlist:
                resultlist.append(u_line[0])
        conn.close()
        return resultlist

    # 获取用户表
    def get_logineduser(self, token):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "SELECT username FROM logined   where logined_token = %s"
        sqldata.append(token)

        cur.execute(sql, sqldata)
        conn.commit()
        tempdict = {}
        u = cur.fetchall()
        for u_line in u:
            tempdict["username"] = u_line[0]
        conn.close()

        return tempdict

    # 登录token，用户删除功能
    def logined_delete(self, logined_token):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "DELETE FROM logined WHERE logined_token = %s"
        sqldata.append(logined_token)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # user表抓包token、有效期编辑功能
    def user_edit(self, requestdict):
        print(requestdict)
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        validtime = requestdict['validtime']
        validtime = datetime_add8(validtime)
        sql = "UPDATE  user SET validtime = %s, capture_token = %s WHERE myuser = %s"
        sqldata.append(validtime)
        sqldata.append(requestdict['capture_token'])
        sqldata.append(requestdict['username'])

        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    def get_config_from_config_name(self, my_config_name):
        conn = self.get_conn()
        cur = conn.cursor()

        sqldata = []
        sql = "SELECT scan_type_name,scan_type_run_name,status,content FROM scan_config   where config_name = %s and status = %s ;"
        sqldata.append(my_config_name)
        sqldata.append("1")
        cur.execute(sql, sqldata)
        conn.commit()
        u1 = cur.fetchall()

        resultdictlist = []
        for u_line in u1:
            tempdict_result = {}
            tempdict_result["scan_type_name"] = u_line[0]
            tempdict_result["scan_type_run_name"] = u_line[1]
            tempdict_result["status"] = u_line[2]
            tempdict_result["content"] = u_line[3]
            resultdict = tempdict_result
            if resultdict not in resultdictlist:
                resultdictlist.append(resultdict)
        cur.close()
        conn.close()
        return resultdictlist

    # return form dict
    def get_config_dict_from_config_name(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        if "search" not in requestdict.keys():
            return {}
        my_config_name = requestdict["search"]
        sqldata = []
        sql = "SELECT scan_type_name,scan_type_run_name,status,content FROM scan_config   where config_name = %s  and username = %s ;"
        sqldata.append(my_config_name)
        sqldata.append(requestdict['username'])
        cur.execute(sql, sqldata)
        conn.commit()
        u1 = cur.fetchall()
        resultdict = {}
        for u_line in u1:
            resultdict["config_name"] = my_config_name
            tempdict = {}
            tempdict["scan_type_name"] = u_line[0]
            resultdict[u_line[0]] = tempdict
            resultdict[u_line[0]]["scan_type_name"] = u_line[0]
            resultdict[u_line[0]]["scan_type_run_name"] = u_line[1]
            temp_status = False
            if u_line[2] == "1":
                temp_status = True
            else:
                temp_status = False
            resultdict[u_line[0]]["status"] = temp_status
            resultdict[u_line[0]]["content"] = json.loads(u_line[3])

        cur.close()
        conn.close()
        return resultdict

    def get_config_from_projectid(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "SELECT config_name FROM project_config   where id = %s"
        sqldata.append(requestdict["id"])
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        u = cur.fetchall()

        for u_line in u:
            tempdict = {}
            tempdict["config_name"] = u_line[0]
        cur.close()
        sqldata.clear()
        cur.close()
        conn.close()
        resultdictlist = self.get_config_from_config_name(tempdict["config_name"])
        return resultdictlist

    def get_project_status(self, status):
        conn = self.get_conn()
        cur = conn.cursor()

        sql = "SELECT id,content,username FROM project_config   where status = %s"
        self.sqldata.append(status)
        cur.execute(sql, self.sqldata)
        conn.commit()
        u = cur.fetchall()

        for u_line in u:
            tempdict = {}
            tempdict["id"] = u_line[0]
            tempdict["project"] = u_line[1]
            tempdict["username"] = u_line[2]  # 抓包认证token
            self.resultlist.append(tempdict)
        cur.close()
        conn.close()
        self.uninit()
        return self.resultlist

    # 设置项目状态，判断是否开启扫描 return list
    def set_project_status(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()

        sql = "UPDATE  project_config SET status = %s  WHERE id = %s"
        self.sqldata.append(requestdict["status"])
        self.sqldata.append(requestdict["id"])
        try:
            cur.execute(sql, self.sqldata)
            conn.commit()
        except Exception as e:
            print(e)
        cur.close()
        conn.close()
        self.uninit()

    # 添加配置
    def add_rule_config(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        print("准备写入")
        print(requestdict)
        write_list = ['Judge_out_of_access', 'Payloadlist_xss', 'Check_sensitive_info', 'Segment', 'Monitor']
        for write_line in write_list:
            data = {
                'scan_type_name': requestdict["add"][write_line]["scan_type_name"],
                'scan_type_run_name': requestdict["add"][write_line]["scan_type_run_name"],
                'status': requestdict["add"][write_line]["status"],
                # 'content': str(requestdict["add"][write_line]["content"]),
                #  json.dumps(bItem, ensure_ascii=False)
                'content': json.dumps(requestdict["add"][write_line]["content"], ensure_ascii=False),
                'username': requestdict["username"],
                'config_name': requestdict["add"]["config_name"],
            }
            table_name = 'scan_config'
            # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
            keys = ', '.join(data.keys())

            values = ', '.join(['%s'] * len(data))

            sql = "REPLACE  INTO {table}({keys}) VALUES ({values})".format(table=table_name, keys=keys, values=values)
            try:
                # 这里的第二个参数传入的要是一个元组
                if cur.execute(sql, tuple(data.values())):
                    print('Successful')
                else:
                    print("not Successful")
            except Exception as e:
                print('Failed')
                print(sql)
                print(data)
                print(type(requestdict[write_line]["content"]))
                print(requestdict[write_line]["content"])
                print(tuple(data.values()))
                print(e)
                conn.rollback()
        conn.commit()
        cur.close()
        conn.close()

    def edit_rule_config(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        print("准备写入")
        print(requestdict)
        write_list = ['Judge_out_of_access', 'Payloadlist_xss', 'Check_sensitive_info', 'Segment', 'Monitor']
        for write_line in write_list:
            data = {
                'scan_type_name': requestdict["edit"]["form"][write_line]["scan_type_name"],
                'scan_type_run_name': requestdict["edit"]["form"][write_line]["scan_type_run_name"],
                'status': requestdict["edit"]["form"][write_line]["status"],
                'content': json.dumps(requestdict["edit"]["form"][write_line]["content"], ensure_ascii=False),
                'username': requestdict["username"],
                'config_name': requestdict["edit"]["form"]["config_name"],
            }
            table_name = 'scan_config'
            sqldata = []
            sqldata.append(data["scan_type_run_name"])
            sqldata.append(data["status"])
            sqldata.append(data["content"])
            sqldata.append(data["config_name"])
            sqldata.append(data["username"])
            sqldata.append(data["scan_type_name"])
            sql = "UPDATE {table} SET scan_type_run_name = %s , status = %s , content = %s where config_name = %s and  username = %s and scan_type_name = %s ;".format(
                table=table_name)
            try:
                print(sql)
                print(sqldata)
                # 这里的第二个参数传入的要是一个元组
                if cur.execute(sql, sqldata):
                    print('Successful')
                else:
                    print("not Successful")
            except Exception as e:
                print('Failed')
                print(sql)
                print(data)
                print(e)
                conn.rollback()
        conn.commit()
        cur.close()
        conn.close()

    def delete_rule_config(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqldata = []
        sql = "DELETE FROM scan_config WHERE username = %s and config_name = %s ;"
        print(sql)
        sqldata.append(str(requestdict["username"]))
        sqldata.append(str(requestdict["delete"]))
        print(sqldata)
        cur.execute(sql, sqldata)
        conn.commit()
        conn.close()

    # dashboard统计
    def data_packet_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT count(id) FROM customers; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT count(id) FROM customers WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        data_count = 0
        for u_line in u:
            data_count = u_line[0]
        conn.close()
        return data_count

    def vulnerable_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        tempdict = copy.deepcopy(requestdict)
        tempdict["total_type"] = "漏洞"
        for keyline, valueline in dict(tempdict).items():
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT count(id) FROM vulnerable; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT count(id) FROM vulnerable WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        data_count = 0
        for u_line in u:
            data_count = u_line[0]
        conn.close()
        return data_count

    def project_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        tempdict = copy.deepcopy(requestdict)
        tempdict["valid"] = 1
        for keyline, valueline in dict(tempdict).items():
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT count(id) FROM project_config; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT count(id) FROM project_config WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        data_count = 0
        for u_line in u:
            data_count = u_line[0]
        conn.close()
        return data_count

    def user_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        tempdict = copy.deepcopy(requestdict)
        tempdict["valid"] = 1
        remove_value = tempdict.pop("username", "404")
        for keyline, valueline in dict(tempdict).items():
            if valueline != "0":  # 判断每一个条件内容
                # # 时间大小比较
                if keyline == "starttime" or keyline == "stoptime":
                    starttimeflag = True
                    continue
                elif keyline == "value":
                    sqlquery.append("(instr(request, %s)  or instr(response, %s))")
                    sqldata.append(valueline)
                    sqldata.append(valueline)
                else:
                    sqlquery.append(str(keyline) + "=%s")
                    sqldata.append(valueline)
        if not sqlquery:
            sql = "SELECT count(myuser) FROM user; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "SELECT count(myuser) FROM user WHERE " + sqlquerystring
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        data_count = 0
        for u_line in u:
            data_count = u_line[0]
        conn.close()
        return data_count

    def data_month_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        for keyline, valueline in dict(requestdict).items():
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        if not sqlquery:
            sql = "select DATE_FORMAT(time,'%%Y%%m') months,count(id) count from customers group by months; "
            # "select DATE_FORMAT(time,'%Y%m') months,count(id) count from customers group by months; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "select DATE_FORMAT(time,'%%Y%%m') months,count(id) count from customers WHERE " + \
                  sqlquerystring + " group by months;"
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        resultdict = {}
        for u_line in u:
            resultdict[u_line[0]] = u_line[1]
        conn.close()
        resultlist = make_year_month_dict(result_dict=resultdict)
        return resultlist

    def vulnerable_month_count(self, requestdict):
        conn = self.get_conn()
        cur = conn.cursor()
        sqlquery = []
        sqldata = []
        tempdict = copy.deepcopy(requestdict)
        tempdict["total_type"] = "漏洞"
        for keyline, valueline in dict(tempdict).items():
            if valueline != "0":  # 判断每一个条件内容
                sqlquery.append(str(keyline) + "=%s")
                sqldata.append(valueline)
        if not sqlquery:
            sql = "select DATE_FORMAT(time,'%%Y%%m') months,count(id) count from vulnerable group by months; "
            # "select DATE_FORMAT(time,'%Y%m') months,count(id) count from customers group by months; "
            cur.execute(sql)
            # todo datetime 搜索
            # return None
        else:
            sqlquerystring = " and ".join(sqlquery)
            # 加上类型 方法
            sql = "select DATE_FORMAT(time,'%%Y%%m') months,count(id) count from vulnerable WHERE " + \
                  sqlquerystring + " group by months;"
            cur.execute(sql, sqldata)

        u = cur.fetchall()
        resultdict = {}
        for u_line in u:
            resultdict[u_line[0]] = u_line[1]
        conn.close()
        resultlist = make_year_month_dict(result_dict=resultdict)
        return resultlist
