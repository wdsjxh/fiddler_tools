import copy
import numpy
from utils.timeutils import datetime_add8
import json
from flask_restful import Api
from flask import Flask
from flask import request
from flask_cors import *
from utils.mysqlutils import mysqlutil
from utils.encryutils import encryutils
from config.dbconfig import dbconfig

app = Flask(__name__)

api = Api(app)
CORS(app, supports_credentials=True)

mysqlutil = mysqlutil()
myencryutils = encryutils()
mydbconfig = dbconfig()


def get_post_data():
    """
    从请求中获取参数
    :return:
    """
    data = {}
    if request.content_type.startswith('application/json'):
        # data = request.get_data()
        data = request.get_data(as_text=True)
        print(type(data))
        print(data)
        try:
            data = json.loads(data, strict=True)
        except Exception as e:
            print(e)
    else:  # urlformed
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
    return data


def get_username_by_request(request):
    try:
        mytoken = request.headers.get('X-Token')
        if not mytoken:
            return None
        else:
            myuserdict = mysqlutil.get_logineduser(mytoken)
            myuser = myuserdict['username']
            return myuser
    except Exception as e:
        print(e)
        return None


@app.route('/data_packet_mul', methods=['GET'])
def data_packet_mul():
    myprojectlist = get_project_by_request(request)
    if myprojectlist is None or len(myprojectlist) == 0:
        myprojectlist = ["default"]
    print(myprojectlist)
    print(request.args.get('method'))
    print(request.args.get('httptype'))
    # 默认第一个

    origin_dict = {}
    requestdict = request.args.to_dict()
    print(requestdict)
    myusername = get_username_by_request(request)
    if requestdict['username'] != myusername:
        requestdict['username'] = myusername

    if "search" in dict(requestdict).keys():
        print("搜索处search")
        removed_search = requestdict.pop('search', '404')
    else:
        print("不是搜索处search")
        # 处理默认project参数   搜索全局时候失效  不开启
        try:
            if requestdict['project'] is None or requestdict['project'] == "0":
                requestdict['project'] = myprojectlist[0]
        except Exception as e:
            print(e)
            requestdict['project'] = myprojectlist[0]
    print(requestdict)
    # 处理时间
    try:
        if requestdict['starttime'] and requestdict['starttime'] != "0":
            requestdict['starttime'] = datetime_add8(requestdict['starttime'])
        if requestdict['stoptime'] and requestdict['starttime'] != "0":
            requestdict['stoptime'] = datetime_add8(requestdict['stoptime'])
    except Exception as e:
        print(e)
    origin_dict = copy.deepcopy(requestdict)
    # print(type(requestdict['starttime']))
    removed_value = requestdict.pop('page', '404')
    removed_value2 = requestdict.pop('limit', '404')
    print(origin_dict)
    totalresultlist = mysqlutil.data_packet_mul(requestdict)
    print(len(totalresultlist))
    resultlist = mysqlutil.data_packet_mullimit(origin_dict)
    return json.dumps(
        {"code": 20000, "data": {"project": myprojectlist, "total": len(totalresultlist), "items": resultlist}})


@app.route('/vulnerable_details_mul')
def vulnerable_details_mul():
    myprojectlist = get_project_by_request(request)
    if myprojectlist is None or len(myprojectlist) == 0:
        myprojectlist = ["default"]
    # 默认第一个

    origin_dict = {}
    requestdict = request.args.to_dict()
    myusername = get_username_by_request(request)
    if requestdict['username'] != myusername:
        requestdict['username'] = myusername

    if "search" in dict(requestdict).keys():
        print("搜索处search")
        removed_search = requestdict.pop('search', '404')
    else:
        print("不是搜索处search")
        # 处理默认project参数   搜索全局时候失效  不开启
        try:
            if requestdict['project'] is None or requestdict['project'] == "0":
                requestdict['project'] = myprojectlist[0]
        except Exception as e:
            print(e)
            requestdict['project'] = myprojectlist[0]
    # 处理时间
    try:
        if requestdict['starttime'] and requestdict['starttime'] != "0":
            requestdict['starttime'] = datetime_add8(requestdict['starttime'])
        if requestdict['stoptime'] and requestdict['starttime'] != "0":
            requestdict['stoptime'] = datetime_add8(requestdict['stoptime'])
    except Exception as e:
        print(e)
    origin_dict = copy.deepcopy(requestdict)
    removed_value = requestdict.pop('page', '404')
    removed_value2 = requestdict.pop('limit', '404')

    all_condition = copy.deepcopy(requestdict)  # 包含 method total_type  details_type

    removed_value3 = requestdict.pop('method', '404')
    removed_value4 = requestdict.pop('total_type', '404')
    removed_value5 = requestdict.pop('details_type', '404')

    mymethod = mysqlutil.vulnerable_details_group_by_method(requestdict)
    print("mymethod 之后")
    print(requestdict)
    mytotal_type = mysqlutil.vulnerable_details_group_by_total_type(requestdict)
    mydetails_type = mysqlutil.vulnerable_details_group_by_details_type(requestdict)

    totalresultlist = mysqlutil.vulnerable_details_mul(all_condition)
    print(len(totalresultlist))
    resultlist = mysqlutil.vulnerable_details_mullimit(origin_dict)
    return json.dumps(
        {"code": 20000, "data": {"project": myprojectlist, "method": mymethod, "details_type": mydetails_type,
                                 "total_type": mytotal_type, "total": len(totalresultlist), "items": resultlist}})


@app.route('/project_config_mul')
def project_config_mul():
    print(request.args.get('page'))
    print(request.args.get('limit'))
    print(request.args.get('type'))
    print(request.args.get('content'))
    print(request.args.get('deleteid'))
    # 添加删除、编辑、添加等操作，之后再查询
    print(request.args.to_dict())

    all_config_name = get_configname_by_request(request)
    print(all_config_name)
    my_origin_dict = {}
    requestdict = request.args.to_dict()
    my_origin_dict = copy.deepcopy(requestdict)  # 最原始版本
    print("project_config_mul")

    myusername = get_username_by_request(request)
    if requestdict['username'] != myusername:
        requestdict['username'] = myusername

    my_removed_token = requestdict.pop('token', '404')

    if request.args.get('deleteid') and request.args.get('deleteid') != "0":
        mysqlutil.project_config_delete_id(requestdict)
        my_removed_value = requestdict.pop('deleteid', '404')
        print("删除后的字典")
    elif request.args.get('edit') and request.args.get('edit') != "0":
        print("后续编辑操作")
        mysqlutil.project_config_edit(requestdict)
        my_removed_value = requestdict.pop('edit', '404')
    elif request.args.get('add') and request.args.get('add') != "0":
        print("后续添加操作")
        mysqlutil.project_add(requestdict)
        my_removed_value = requestdict.pop('add', '404')
    elif request.args.get('bind_config') and request.args.get('bind_config') != "0":
        print("后续绑定配置操作")
        print(requestdict)
        mysqlutil.project_config_bind(requestdict)
        my_removed_value = requestdict.pop('bind_config', '404')
    if request.args.get('start') and request.args.get('start') != "0":
        print(request.args.get('start'))
        print(type(request.args.get('start')))

        print("后续启动扫描操作")
        pro_name_dict = {}
        pro_name_dict["status"] = "scanning"
        startid = request.args.get('startid')
        print(type(startid))
        pro_name_dict["id"] = int(startid)
        pro_name_dict["project"] = request.args.get('start')
        pro_name_dict["username"] = requestdict['username']
        print(requestdict)
        mysqlutil.set_project_status(pro_name_dict)
        my_removed_value = requestdict.pop('start', '404')
        my_removed_startid = requestdict.pop('startid', '404')
        print(requestdict)

    origin_dict = copy.deepcopy(requestdict)
    removed_value = requestdict.pop('page', '404')
    removed_value2 = requestdict.pop('limit', '404')
    totalresultlist = mysqlutil.project_config_mul(requestdict)
    resultlist = mysqlutil.project_config_mullimit(origin_dict)
    return json.dumps({"code": 20000, "data": {"total": len(totalresultlist), "items": resultlist,
                                               "all_config_name": all_config_name}})


@app.route('/user_config_mul')
def user_config_mul():
    # 添加删除、编辑、添加等操作，之后再查询
    print(request.args.to_dict())

    my_origin_dict = {}
    requestdict = request.args.to_dict()
    print(requestdict)
    my_origin_dict = copy.deepcopy(requestdict)  # 最原始版本
    print(requestdict)
    print("user_config_mul")

    # flag 存在   需要使用  传过来的默认username
    # 不存在，需要把原来的username 删掉
    myusername = get_username_by_request(request)

    # 判断用户权限
    myrole = ""
    myuser_role_dict = mysqlutil.get_user_role(myusername)
    if "roles" in myuser_role_dict.keys() and myuser_role_dict["roles"] is not None:
        myrole = myuser_role_dict["roles"]
        if myuser_role_dict["roles"] == "user":
            return json.dumps({"code": 50000, "message": "没有访问权限"})

    if requestdict['username'] != myusername:
        requestdict['username'] = myusername

    my_removed_username = requestdict.pop('username', '404')

    my_removed_token = requestdict.pop('token', '404')
    print("删除username后的")
    print(requestdict)

    if request.args.get('delete_user') and request.args.get('delete_user') != "0":
        print("后续删除操作")
        mydelete_role_dict = mysqlutil.get_user_role(requestdict["delete_user"])
        mydelete_role_user = mydelete_role_dict["roles"]
        if mydelete_role_user != "user" and myrole == "admin":
            return json.dumps({"code": 50000, "message": "没有操作权限"})
        mysqlutil.user_config_delete_user(requestdict)
        my_removed_value = requestdict.pop('delete_user', '404')
        print("删除后的字典")
        print(requestdict)
    elif request.args.get('edit') and request.args.get('edit') != "0":
        print("后续编辑操作")
        mydict = json.loads(requestdict["edit"])
        if mydict["roles"] != "user" and myrole == "admin":
            return json.dumps({"code": 50000, "message": "没有操作权限"})
        mysqlutil.user_config_edit(mydict)
        print(requestdict)
        my_removed_value = requestdict.pop('edit', '404')
    elif request.args.get('add') and request.args.get('add') != "0":
        print("后续添加操作")
        mydict = json.loads(requestdict["add"])
        if mydict["roles"] != "user" and myrole == "admin":
            return json.dumps({"code": 50000, "message": "没有操作权限"})
        addresultdict = mysqlutil.adduser_from_backend(mydict)
        print(addresultdict)
        my_removed_value = requestdict.pop('add', '404')

    origin_dict = copy.deepcopy(requestdict)
    removed_value = requestdict.pop('page', '404')
    removed_value2 = requestdict.pop('limit', '404')
    totalresultlist = mysqlutil.user_config_mul(requestdict)
    resultlist = mysqlutil.user_config_mullimit(origin_dict)
    return json.dumps({"code": 20000, "data": {"total": len(totalresultlist), "items": resultlist,
                                               }})


# 添加搜索条件的
@app.route('/vulnerable_config_mul')
def vulnerable_config_mul():
    print(request.args.get('page'))
    print(request.args.get('limit'))
    # 添加删除、编辑、添加等操作，之后再查询

    my_origin_dict = {}
    requestdict = request.args.to_dict()

    myusername = get_username_by_request(request)
    if "username" not in requestdict.keys() or requestdict['username'] != myusername:
        requestdict['username'] = myusername

    my_origin_dict = copy.deepcopy(requestdict)  # 最原始版本
    print(requestdict)

    if request.args.get('deleteid') and request.args.get('deleteid') != "0":
        mysqlutil.config_delete_id(requestdict)
        my_removed_value = requestdict.pop('deleteid', '404')
        print("删除后的字典")
        print(requestdict)
    elif request.args.get('edit') and request.args.get('edit') != "0":
        print(request.args.get('edit'))
        print(type(request.args.get('edit')))
        print("后续编辑操作")
        # 涉及到其他表数据字段
        mysqlutil.config_edit(requestdict)
        my_removed_value = requestdict.pop('edit', '404')
        print(requestdict)
    elif request.args.get('add') and request.args.get('add') != "0":
        print(request.args.get('add'))
        print(type(request.args.get('add')))
        print("后续添加操作")
        mysqlutil.config_add(requestdict)
        my_removed_value = requestdict.pop('add', '404')
        print(requestdict)

    origin_dict = {}
    print(requestdict)

    origin_dict = copy.deepcopy(requestdict)

    removed_value = requestdict.pop('page', '404')
    print(requestdict)
    removed_value2 = requestdict.pop('limit', '404')
    print(requestdict)
    print(origin_dict)
    totalresultlist = mysqlutil.vulnerable_config_mul(requestdict)
    print(len(totalresultlist))
    resultlist = mysqlutil.vulnerable_config_mullimit(origin_dict)
    return json.dumps({"code": 20000, "data": {"total": len(totalresultlist), "items": resultlist}})


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        requestdict = get_post_data()
        # print(requestdict)
        if not requestdict['username'] or not requestdict['password'] or len(str(requestdict['username'])) == 0 or len(
                str(requestdict['password'])) == 0:
            return json.dumps({"code": 50000, "message": "用户名或密码为空"})
        else:
            myusername = requestdict['username']
            mypassword = requestdict['password']

            mypasssaltroledict = mysqlutil.get_userinfo(myusername)
            print(mypasssaltroledict)
            if not mypasssaltroledict:
                return json.dumps({"code": 50043, "message": "账号密码不正确"})
            else:
                resultpass = myencryutils.passwordenc(mypassword, mypasssaltroledict["salt"])
                # print(resultpass)
                if resultpass == mypasssaltroledict["password"]:
                    # print("登录成功")
                    # print(type(requestdict))
                    tokendata = myencryutils.newtoken(myusername, str(mypasssaltroledict["salt"])[-6:])
                    mysqlutil.add_logineduser(tokendata, myusername)
                    # print(tokendata)
                    return json.dumps({"code": 20000, "data": {"token": tokendata}})
                else:
                    return json.dumps({"code": 50043, "message": "账号密码不正确"})
    elif request.method == 'GET':
        return json.dumps({"code": 200, "message": "GET"})


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        requestdict = get_post_data()
        # print(requestdict)
        if not requestdict['username'] or not requestdict['password'] or len(str(requestdict['username'])) == 0 or len(
                str(requestdict['password'])) == 0:
            return json.dumps({"code": 50000, "data": {"message": "用户名或密码为空"}})
        else:
            myusername = requestdict['username']
            mypassword = requestdict['password']

            resultdict = mysqlutil.adduser(myusername, mypassword, "user")
            print(requestdict)
            return json.dumps(resultdict)


@app.route('/user/info', methods=['GET'])
def get_info():
    if request.method == 'GET':
        requestdict = request.args.to_dict()
        print(requestdict)
        print(type(requestdict))
        # 从登录表找到user，然后读用户表信息
        if not requestdict["token"]:
            return json.dumps({"code": 50000, "message": "没有读到token"})
        else:
            my_token_user_dict = mysqlutil.get_logineduser(requestdict["token"])
            print(type(my_token_user_dict))
            print(my_token_user_dict)
            my_user = my_token_user_dict["username"]
            my_userinfo = mysqlutil.get_userinfo(my_user)

            return json.dumps({"code": 20000,
                               "data": {"name": my_user,
                                        "roles": my_userinfo["roles"],
                                        "avatar": my_userinfo["avatar"],
                                        "introduction": my_userinfo["introduction"]
                                        }
                               })


@app.route('/user/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        try:
            mytoken = request.headers.get('X-Token')
            if not mytoken:
                return json.dumps({"code": 50000, "data": "failed"})
            else:
                mysqlutil.logined_delete(mytoken)
        except Exception as e:
            print(e)
        return json.dumps({"code": 20000, "data": "success"})


# request return project names
def get_project_by_request(request):
    myuser = get_username_by_request(request)
    myprojectlist = mysqlutil.get_projectname_by_username(myuser)
    return myprojectlist


def get_configname_by_request(request):
    myuser = get_username_by_request(request)
    my_configname_list = mysqlutil.get_configname_by_username(myuser)
    return my_configname_list


@app.route('/user/make_capture_token', methods=['POST'])
def make_capture_token():
    myapi = mydbconfig.getmyapi() + "/api/deal_capture_token" + "|"
    # myapi = "http://172.31.61.132:5000/api/deal_capture_token" + "|"
    if request.method == 'POST':
        requestdict = get_post_data()
        print(requestdict)
        if not requestdict['name'] or not requestdict['token'] or len(str(requestdict['name'])) == 0 or len(
                str(requestdict['token'])) == 0:
            return json.dumps({"code": 50000, "data": "参数异常"})
        else:
            myname = requestdict['name']
            mytoken = requestdict['token']

            myusername = get_username_by_request(request)
            if myname != myusername:
                myname = myusername

            if requestdict['createflag'] == '0':
                # 查询token显示
                print("查询")
                tempresult = mysqlutil.get_userinfo(myname)
                return json.dumps(
                    {"code": 20000, "data": "success",
                     "capture_token": myapi + tempresult["capture_token"]})
            else:
                if requestdict['date']:
                    mydate = requestdict['date']
                else:
                    return json.dumps({"code": 50000, "data": "failed", "message": "日期为空"})
                try:
                    mytokens = request.headers.get('X-Token')
                    if not mytokens:
                        return json.dumps({"code": 50000, "data": "failed"})
                    else:
                        print("生成token")
                        my_capture_token = myencryutils.new_capture_token(myname, mytoken)
                        tempdict = {}
                        tempdict['capture_token'] = my_capture_token
                        tempdict['username'] = myname
                        tempdict['validtime'] = mydate
                        # 写入
                        mysqlutil.user_edit(tempdict)
                        # return json.dumps({"code": 20000, "data": "success", "capture_token": my_capture_token})
                except Exception as e:
                    print(e)
                    return json.dumps({"code": 50000, "data": "failed"})
                return json.dumps(
                    {"code": 20000, "data": "success",
                     "capture_token": myapi + my_capture_token})


# token 返回 用户名 项目名
@app.route('/api/deal_capture_token', methods=['POST', 'GET'])
def deal_capture_token():
    # print(request)
    if request.method == 'POST':
        requestdict = get_post_data()
        print(requestdict)
        if not requestdict['token'] or len(str(requestdict['token'])) == 0:
            return json.dumps({"code": 50000, "data": "token参数异常"})
        else:
            mytoken = requestdict['token']

            print("校验token，获取用户名和项目名")
            print(mytoken)
            tempdict = mysqlutil.get_userby_capture_token(mytoken)
            try:
                myname = tempdict['username']
                if not myname or len(str(myname)) == 0:
                    return json.dumps({"code": 50000, "data": "failed"})
                else:
                    print(myname)
                    myprojectlist = mysqlutil.get_projectname_by_username(myname)
                    print(myprojectlist)

                    ##
                    requestdict = {}
                    requestdict["username"] = myname
                    resultdict = mysqlutil.get_config(requestdict)  # 配置名
                    ##

            except Exception as e:
                print(e)
                return json.dumps({"code": 50000, "data": "failed"})
            return json.dumps({"code": 20000, "data": "success", "username": myname, "project_names": myprojectlist,
                               "result": resultdict})
    elif request.method == 'GET':
        print("get")
        return json.dumps({"code": 20000, "data": "success"})


@app.route('/api/deal_post_data', methods=['POST'])
def deal_post_data():
    if request.method == 'POST':
        try:
            requestdict = get_post_data()
            # print(requestdict)
        except:
            return json.dumps({"code": 50000, "data": "获取原始数据失败"})
        if not requestdict['token'] or len(str(requestdict['token'])) == 0:
            return json.dumps({"code": 50000, "data": "token参数异常"})
        else:
            mytoken = requestdict['token']
            tempdict = mysqlutil.get_userby_capture_token(mytoken)
            try:
                myname = tempdict['username']
                if not myname or len(str(myname)) == 0:
                    return json.dumps({"code": 50000, "data": "failed"})
                else:
                    mysqlutil.add_packet(requestdict)
            except Exception as e:
                print(e)
                return json.dumps({"code": 50000, "data": "failed"})
            return json.dumps({"code": 20000, "data": "success"})


# 添加配置
@app.route('/add_rule_config', methods=['POST'])
def add_rule_config():
    if request.method == 'POST':

        try:
            requestdict = get_post_data()
            print(requestdict)
        except:
            return json.dumps({"code": 50000, "data": "获取原始数据失败"})
        if not requestdict['token'] or len(str(requestdict['token'])) == 0:
            return json.dumps({"code": 50000, "data": "token参数异常"})
        else:
            form = {}
            myusername = get_username_by_request(request)
            if requestdict['username'] != myusername:
                requestdict['username'] = myusername

            if "add" in requestdict.keys() and requestdict["add"] and request.args.get('add') != "0":
                print("后续添加配置操作")
                print(requestdict)
                mysqlutil.add_rule_config(requestdict)
                my_removed_value = requestdict.pop('add', '404')
            elif "edit" in requestdict.keys() and requestdict["edit"] and request.args.get('edit') != "0":
                if requestdict["edit"]["origin_configname"] != requestdict["edit"]["form"]["config_name"]:
                    return json.dumps({"code": 50000, "data": "编辑配置名不可修改"})
                else:
                    print("后续编辑配置操作")
                    print(requestdict)
                    mysqlutil.edit_rule_config(requestdict)
                    my_removed_value = requestdict.pop('edit', '404')
            elif "delete" in requestdict.keys() and requestdict["delete"] and request.args.get('delete') != "0":
                print("后续删除配置操作")
                print(requestdict)
                mysqlutil.delete_rule_config(requestdict)
                my_removed_value = requestdict.pop('delete', '404')
            elif "search" in requestdict.keys() and requestdict["search"] and request.args.get('search') != "0":
                print("后续查询配置操作")
                print(requestdict)
                form = mysqlutil.get_config_dict_from_config_name(requestdict)
                print(form)
                my_removed_value = requestdict.pop('search', '404')

            myconfignamelist = get_configname_by_request(request)
            if myconfignamelist is None or len(myconfignamelist) == 0:
                myconfignamelist = ["默认配置"]

            return json.dumps(
                {"code": 20000, "data": {"message": "success", "items": form}, "myconfignamelist": myconfignamelist})


# token 返回 用户名 项目名
@app.route('/api/get_config', methods=['POST'])
def get_config():
    if request.method == 'POST':
        try:
            requestdict = get_post_data()
        except:
            return json.dumps({"code": 50000, "data": "获取原始数据失败"})

        if not requestdict['token'] or len(str(requestdict['token'])) == 0:
            return json.dumps({"code": 50000, "data": "token参数异常"})
        else:
            mytoken = requestdict['token']
            tempdict = mysqlutil.get_userby_capture_token(mytoken)
            try:
                myname = tempdict['username']
                if not myname or len(str(myname)) == 0:
                    return json.dumps({"code": 50000, "data": "failed"})
                else:
                    # 具体逻辑
                    requestdict = {}
                    requestdict["username"] = myname
                    resultdict = mysqlutil.get_config(requestdict)
                    # print(resultdict)
            except Exception as e:
                print(e)
                return json.dumps({"code": 50000, "data": "failed"})
            allresult = json.dumps({"code": 20000, "data": "success", "result": resultdict})
            return allresult


# dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # 默认第一个
    origin_dict = {}
    requestdict = request.args.to_dict()
    print(requestdict)
    myusername = get_username_by_request(request)
    print(myusername)
    myuser_role_dict = mysqlutil.get_user_role(myusername)

    if not myusername:
        return json.dumps({"code": 50000, "data": "failed"})
    try:
        if requestdict['username'] != myusername or 'username' not in dict(requestdict).keys():
            requestdict['username'] = myusername
    except Exception as e:
        print(e)
        requestdict['username'] = myusername

    data_packet_count = mysqlutil.data_packet_count(requestdict)
    vulnerable_count = mysqlutil.vulnerable_count(requestdict)
    project_count = mysqlutil.project_count(requestdict)

    data_month_count = mysqlutil.data_month_count(requestdict)
    vulnerable_month_count = mysqlutil.vulnerable_month_count(requestdict)
    normal_month_count = numpy.array(data_month_count) - numpy.array(vulnerable_month_count)
    normal_month_count = normal_month_count.tolist()

    result_dict = {"code": 20000,
                   "data":
                       {"data_packet_count": int(data_packet_count),
                        "vulnerable_count": int(vulnerable_count),
                        "project_count": int(project_count),
                        "data_month_count": data_month_count,
                        "vulnerable_month_count": vulnerable_month_count,
                        "normal_month_count": normal_month_count
                        }}
    if "roles" in myuser_role_dict.keys() and myuser_role_dict["roles"] is not None:
        if myuser_role_dict["roles"] == "user":
            pass
        else:
            user_count = mysqlutil.user_count(requestdict)
            result_dict["data"]["user_count"] = int(user_count)
    print('dashboard return')
    print(result_dict)
    return json.dumps(result_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
