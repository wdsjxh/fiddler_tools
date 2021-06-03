# coding:utf-8
from utils.deal_dict_class import returnjson_payload
from utils.deal_dict_class import returnreplacejson_payload
import json
from data.myData import myData
import requests
from utils import makepayloadstring
from utils.dealencode import dealstringencode
from utils.dealexceptvul import dealexpvul
from utils.dealduplicate import dealduplicate
from utils.mysqlutils import mysqlutil
from utils.dealstring import is_only_onestring
from utils.dealrequest import dealrequest
from utils import charsetutils

test_request_response_dict = {}

mydealexpvul = dealexpvul()
mydealduplicate = dealduplicate()  # 判断重复数据包
mysqlutil = mysqlutil()
dealrequest = dealrequest()


# json返回包替换时间戳 返回字典
def json_no_timestamp(jsonstring, uidstring):
    if not jsonstring:
        return None
    try:
        dict_json = json.loads(jsonstring)
    except Exception as e:
        print(e)
        return {}

    tempresult = returnreplacejson_payload(
        dict_json, "timestamp",
        uidstring)
    if len(tempresult) == 0:  # 没有时间戳等其他字符串  默认返回是list
        dict_no_timestamp = dict_json
    else:
        dict_no_timestamp = tempresult[0]
    return dict_no_timestamp


def judge_out_of_access(requestdict):
    request_url = ""
    my_temp_id = 0
    my_time = ""
    global_data = myData()

    total_type = "漏洞"
    details_type = "越权"

    judge_out_of_access_flag = "judge_out_of_access"
    my_request_data_list = []  # 根据请求包去重
    my_expect_request_list = mysqlutil.get_request_customers_exp(requestdict)
    my_request_list = mysqlutil.get_most_customers(requestdict)
    for line in my_request_list:
        my_temp_method = line["method"]
        my_request_data = line["request"]
        my_temp_id = line["id"]
        my_time = line["time"]
        my_httptype = line["httptype"]

        # 判断重复数据请求包
        if mydealduplicate.dealduplicatemain(str(my_request_data)):
            print("重复数据包")
            continue

        if my_request_data not in my_request_data_list:
            my_request_data_list.append(my_request_data)
        else:

            continue

        if my_request_data in my_expect_request_list:
            continue

        request_url_host, request_url_path, header_list, contenttypestring = dealrequest.get_host_uri_header_type(
            my_request_data, my_temp_method)

        if my_httptype == "http" or my_httptype == "https":
            my_url = my_httptype + "://" + request_url_host + request_url_path
        else:
            print("非http https数据包")
            continue
        (request_post_data, my_origin_cookie, header_result) = dealrequest.get_headers(header_list, my_temp_method)
        if not header_result:
            # if (not request_post_data) or (not my_origin_cookie) or (not header_result):
            print("没有post数据包or cookieor header头")
            continue

        request_dict_cookie = dealrequest.get_cookie(my_origin_cookie)

        result_data = ""  # 漏洞内容

        url_path_string = ""
        url_path_parama = ""
        url_path_payload = request_url_path.split("?")

        if len(url_path_payload) == 2:

            url_path_string = url_path_payload[0]

            url_path_parama = url_path_payload[-1]

        elif len(url_path_payload) == 3:

            url_path_string = str(url_path_payload[0]) + "?" + str(url_path_payload[1])
            url_path_parama = url_path_payload[-1]

        elif len(url_path_payload) == 1:

            url_path_string = "".join(url_path_payload)

        if my_temp_method == "POST":
            if len(url_path_payload) == 1 and (
                    request_post_data is None or request_post_data == "" or len(request_post_data) == 0):
                continue
            # contenttypestring
            if 'Content-Type: application/x-www-form-urlencoded' in contenttypestring or contenttypestring == "":
                # post 参数转换
                if len(url_path_payload) > 1 and (
                        request_post_data is None or request_post_data == "" or len(request_post_data) == 0):
                    request_post_data = url_path_parama
                try:
                    if request_dict_cookie:
                        my_origin_response = requests.post(
                            url=my_url,
                            headers=header_result, cookies=request_dict_cookie, data=str(request_post_data))
                    else:
                        my_origin_response = requests.post(
                            url=my_url,
                            headers=header_result, data=str(request_post_data))

                    my_origin_response_coded = charsetutils.checkwebsitecharset(my_origin_response.content)

                    # todo 逐步替换userid参数，判断越权，后期会更复杂的替换数字串判断
                    # 目前是根据替换返回包是否一样判断  后续还得判断  返回包根据uid变化的情况
                    # 返回包不一样默认为存在越权，一样就略过，待测试

                    # 特定字符串匹配到才替换，也有可能是 uid=xss2135345 xss情况
                    if global_data.origin_userid in str(request_post_data):
                        print("user id 在request post data里面 x-www-form-urlencoded")
                        if is_only_onestring(str(request_post_data), global_data.origin_userid):
                            print("只有一个在www-from")
                            mypayloadlist = [
                                str(request_post_data).replace(global_data.origin_userid, global_data.userid_first)]
                            mypayloadlist2 = [
                                str(request_post_data).replace(global_data.origin_userid,
                                                               global_data.userid_second)]

                        else:
                            mypayloadlist = makepayloadstring.makereplacestring(str(request_post_data),
                                                                                global_data.userid_first,
                                                                                my_temp_method,
                                                                                "normal", global_data.origin_userid)
                            mypayloadlist2 = makepayloadstring.makereplacestring(str(request_post_data),
                                                                                 global_data.userid_second,
                                                                                 my_temp_method,
                                                                                 "normal",
                                                                                 global_data.origin_userid)
                        counter = 0
                        for payloadline in mypayloadlist:
                            my_replaceid_response = requests.post(
                                url=my_url,
                                headers=header_result, cookies=request_dict_cookie, data=payloadline)
                            my_replaceid_response2 = requests.post(
                                url=my_url,
                                headers=header_result, cookies=request_dict_cookie, data=mypayloadlist2[counter])

                            my_replaceid_response_coded = charsetutils.checkwebsitecharset(
                                my_replaceid_response.content)
                            if mydealexpvul.dealexpoutofaccess(
                                    my_replaceid_response.content.decode(
                                        "utf-8")) or mydealexpvul.dealexpoutofaccess(
                                my_replaceid_response2.content.decode("utf-8")):
                                continue

                            if json_no_timestamp(my_origin_response_coded,
                                                 global_data.origin_userid) != json_no_timestamp(
                                my_replaceid_response_coded, global_data.userid_first) and json_no_timestamp(
                                charsetutils.checkwebsitecharset(my_replaceid_response2.content),
                                global_data.userid_second) != json_no_timestamp(my_replaceid_response_coded,
                                                                                global_data.userid_first):
                                print("存在越权_userid " + global_data.userid_first)
                                result_data = "存在越权_userid " + global_data.userid_first
                                if result_data != "" and result_data is not None and result_data != " ":
                                    mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                        judge_out_of_access_flag,
                                                                        my_temp_id,
                                                                        my_time,
                                                                        my_request_data,
                                                                        my_origin_response_coded,
                                                                        my_temp_method, result_data)
                                    test_request_response_dict[my_request_data] = result_data
                            counter = counter + 1
                    else:
                        print("user id 不在request post data里面")

                    if charsetutils.checkwebsitecharset(
                            my_origin_response.content) is None or charsetutils.checkwebsitecharset(
                        my_origin_response.content) == "" or request_dict_cookie == {}:
                        continue
                    my_empty_response = requests.post(
                        url=my_url,
                        headers=header_result, cookies="", data=request_post_data)

                    if charsetutils.checkwebsitecharset(
                            my_empty_response.content) is None or charsetutils.checkwebsitecharset(
                        my_empty_response.content) == "":
                        continue

                    cookie_first = global_data.get_cookie_first()

                    my_cookie_first_response = requests.post(
                        url=my_url,
                        headers=header_result, cookies=dealrequest.get_cookie(cookie_first), data=request_post_data)

                    if charsetutils.checkwebsitecharset(
                            my_cookie_first_response.content) is None or charsetutils.checkwebsitecharset(
                        my_cookie_first_response.content) == "":
                        print("my_cookie_first_response为空或者返回包为空")
                        continue

                    if my_origin_response.content == my_empty_response.content:
                        result_data = result_data + " " + "存在越权_空cookie"


                    else:
                        print("不存在越权_空cookie")
                    if my_origin_response.content == my_cookie_first_response.content:
                        print("存在越权_cookie_first")
                        result_data = result_data + " " + "存在越权_cookie_first"

                    # test_request_response.append(my_request_data)
                    if result_data != "" and result_data is not None and result_data != " ":
                        # 插入漏洞表
                        mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                            judge_out_of_access_flag, my_temp_id,
                                                            my_time,
                                                            my_request_data,
                                                            my_origin_response_coded,
                                                            my_temp_method, result_data)
                        test_request_response_dict[my_request_data] = result_data
                except Exception as e:
                    print("请求异常")
                    print(e)

            elif 'application/json' in contenttypestring:
                try:
                    # from urllib.parse import quote
                    # request_dict_cookie = quote(request_dict_cookie, 'utf-8')
                    import chardet

                    if request_dict_cookie or request_dict_cookie != {}:
                        my_origin_response = requests.post(
                            url=my_url,
                            headers=header_result, cookies=request_dict_cookie, json=request_post_data)
                    else:
                        my_origin_response = requests.post(url=my_url, data=request_post_data, headers=header_result,
                                                           timeout=5)

                    my_origin_response_coded = charsetutils.checkwebsitecharset(my_origin_response.content)
                    if my_origin_response_coded is None or my_origin_response_coded == "":
                        continue

                    # 逐步替换userid参数，判断越权，后期会更复杂的替换数字串判断
                    # 特定字符串匹配到才替换，也有可能是 uid=xss2135345 xss情况
                    if global_data.origin_userid in str(request_post_data):
                        if is_only_onestring(str(request_post_data), global_data.origin_userid):
                            json_list = [json.loads(
                                str(request_post_data).replace(global_data.origin_userid, global_data.userid_first))]
                            json_list2 = [json.loads(
                                str(request_post_data).replace(global_data.origin_userid, global_data.userid_second))]
                        else:

                            request_post_data_dict = json.loads(request_post_data)
                            json_list = returnreplacejson_payload(request_post_data_dict, global_data.userid_first,
                                                                  global_data.origin_userid)
                            json_list2 = returnreplacejson_payload(request_post_data_dict, global_data.userid_second,
                                                                   global_data.origin_userid)
                        counter = 0
                        if json_list:
                            for payloadline in json_list:
                                print(payloadline)
                                my_replaceid_response = requests.post(
                                    url=my_url,
                                    headers=header_result, cookies=request_dict_cookie, json=payloadline)
                                my_replaceid_response2 = requests.post(
                                    url=my_url,
                                    headers=header_result, cookies=request_dict_cookie, json=json_list2[counter])

                                my_replaceid_response_coded = charsetutils.checkwebsitecharset(
                                    my_replaceid_response.content)

                                if mydealexpvul.dealexpoutofaccess(my_replaceid_response.content.decode(
                                        "utf-8")) or mydealexpvul.dealexpoutofaccess(
                                    my_replaceid_response2.content.decode("utf-8")):
                                    continue

                                if json_no_timestamp(my_origin_response_coded,
                                                     global_data.origin_userid) != json_no_timestamp(
                                    my_replaceid_response_coded, global_data.userid_first) and json_no_timestamp(
                                    charsetutils.checkwebsitecharset(my_replaceid_response2.content),
                                    global_data.userid_second) != json_no_timestamp(my_replaceid_response_coded,
                                                                                    global_data.userid_first):
                                    print("存在越权_userid " + global_data.userid_first)
                                    result_data = "存在越权_userid " + global_data.userid_first
                                    if result_data != "" and result_data is not None and result_data != " ":
                                        mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                            judge_out_of_access_flag,
                                                                            my_temp_id,
                                                                            my_time,
                                                                            my_request_data,
                                                                            my_origin_response_coded,
                                                                            my_temp_method, result_data)
                                        test_request_response_dict[my_request_data] = result_data

                                counter = counter + 1
                        else:
                            print("json_list为空")
                    else:
                        print("user id 不在request post data里面")

                    # if my_origin_response.content is None or my_origin_response.content == "":
                    if request_dict_cookie == {}:
                        print("cookie为空或者返回包为空")
                        continue
                    my_empty_response = requests.post(
                        url=my_url,
                        headers=header_result, cookies="", json=request_post_data)
                    print("response empty")

                    if charsetutils.checkwebsitecharset(
                            my_empty_response.content) is None or charsetutils.checkwebsitecharset(
                        my_empty_response.content) == "":
                        print("my_empty_response为空或者返回包为空")
                        continue
                    # print(my_empty_response.content.decode())

                    cookie_first = global_data.get_cookie_first()
                    # print ("cookie first")
                    # print(get_cookie(cookie_first))
                    my_cookie_first_response = requests.post(
                        url=my_url,
                        headers=header_result, cookies=dealrequest.get_cookie(cookie_first), json=request_post_data)

                    if charsetutils.checkwebsitecharset(
                            my_cookie_first_response.content) is None or charsetutils.checkwebsitecharset(
                        my_cookie_first_response.content) == "":
                        print("my_cookie_first_response为空或者返回包为空")
                        continue
                    if my_origin_response.content == my_empty_response.content:
                        result_data = result_data + " " + "存在越权_空cookie"

                    else:
                        print("不存在越权_空cookie")
                    if my_origin_response.content == my_cookie_first_response.content:
                        print("存在越权_cookie_first")
                        result_data = result_data + " " + "存在越权_cookie_first"

                    if result_data != "" and result_data is not None and result_data != " ":
                        # 插入漏洞表
                        mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                            judge_out_of_access_flag, my_temp_id, my_time,
                                                            my_request_data,
                                                            my_origin_response_coded,
                                                            my_temp_method, result_data)
                        test_request_response_dict[my_request_data] = result_data
                except Exception as e:
                    print("请求异常")
                    print(e)

        elif my_temp_method == "GET":
            try:
                my_origin_response = requests.get(
                    url=my_url,
                    headers=header_result, cookies=request_dict_cookie, timeout=(3, 7))
            except Exception as e:
                print(e)

            my_origin_response_coded = charsetutils.checkwebsitecharset(my_origin_response.content)
            if len(url_path_payload) < 2:
                # GET请求  伪静态等特殊情况  GET /chatserver/app/api/user/180052/
                # 需要判断普通后端语言没有参数和伪静态
                # .do .action
                myliststr = ""
                langlist = ["jsp", "php", "asp", "aspx", "ashx"]
                myurl_path_payload = "".join(url_path_payload)
                if myurl_path_payload[-1] == "/":
                    myliststr = myurl_path_payload[:-1]
                if myurl_path_payload[0] == "/":
                    myliststr = myliststr[1:]

                mylistsplit = myliststr.split(".")
                print(mylistsplit[-1])
                if mylistsplit[-1] not in langlist:
                    print("not in 需要判断伪静态情况")  #
                    # /fsdf/fsdfg/frh/fsdf.html 情况

                    if global_data.origin_userid in str(myliststr):
                        print("user id 在request get data里面 伪静态")
                        if is_only_onestring(str(myliststr), global_data.origin_userid):
                            mypayloadlist = [
                                str(myliststr).replace(global_data.origin_userid, global_data.userid_first)]
                            mypayloadlist2 = [
                                str(myliststr).replace(global_data.origin_userid, global_data.userid_second)]
                        else:
                            mypayloadlist = makepayloadstring.makerewritestring(str(myliststr),
                                                                                global_data.userid_first,
                                                                                my_temp_method,
                                                                                "normal", global_data.origin_userid)

                            mypayloadlist2 = makepayloadstring.makerewritestring(str(myliststr),
                                                                                 global_data.userid_second,
                                                                                 my_temp_method,
                                                                                 "normal", global_data.origin_userid)
                        counter = 0
                        for payloadline in mypayloadlist:

                            add_replace_my_url = str(
                                my_httptype) + "://" + request_url_host + "/" + payloadline
                            print("伪静态请求url")
                            print(add_replace_my_url)
                            my_replaceid_response = requests.get(
                                url=add_replace_my_url,
                                headers=header_result, cookies=request_dict_cookie, timeout=(3, 7))

                            add_replace_my_url2 = str(
                                my_httptype) + "://" + request_url_host + "/" + mypayloadlist2[counter]
                            my_replaceid_response2 = requests.get(
                                url=add_replace_my_url2,
                                headers=header_result, cookies=request_dict_cookie, timeout=(3, 7))

                            my_replaceid_response_coded = charsetutils.checkwebsitecharset(
                                my_replaceid_response.content)

                            print("替换uid后返回值")
                            # print(add_replace_my_url)
                            # print(my_replaceid_response.content.decode("utf-8"))
                            if mydealexpvul.dealexpoutofaccess(
                                    my_replaceid_response.content.decode(
                                        "utf-8")) or mydealexpvul.dealexpoutofaccess(
                                my_replaceid_response2.content.decode("utf-8")):
                                print("权限无效等")
                                continue

                            if json_no_timestamp(my_origin_response_coded,
                                                 global_data.origin_userid) != json_no_timestamp(
                                my_replaceid_response_coded, global_data.userid_first) and json_no_timestamp(
                                charsetutils.checkwebsitecharset(my_replaceid_response2.content),
                                global_data.userid_second) != json_no_timestamp(my_replaceid_response_coded,
                                                                                global_data.userid_first):
                                print("存在越权_userid " + global_data.userid_first)
                                result_data = "存在越权_userid " + global_data.userid_first
                                if result_data != "" and result_data is not None and result_data != " ":
                                    mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                        judge_out_of_access_flag,
                                                                        my_temp_id,
                                                                        my_time,
                                                                        my_request_data,
                                                                        my_origin_response_coded,
                                                                        my_temp_method, result_data)
                                    test_request_response_dict[my_request_data] = result_data
                            counter = counter + 1
                    else:
                        print("user id 不在request post data里面")

                    print("response")
                    if charsetutils.checkwebsitecharset(
                            my_origin_response.content) is None or charsetutils.checkwebsitecharset(
                        my_origin_response.content) == "" or request_dict_cookie == {}:
                        # str(origin_response.decode())
                        print("cookie为空或者返回包为空")
                        continue
                    try:
                        my_empty_response = requests.get(
                            url=my_url,
                            headers=header_result, cookies="")
                    except:
                        continue
                    print("response empty")
                    if charsetutils.checkwebsitecharset(
                            my_empty_response.content) is None or charsetutils.checkwebsitecharset(
                        my_empty_response.content) == "":
                        print("my_empty_response为空或者返回包为空")
                        continue
                    # print(my_empty_response.content.decode())

                    # global_data = myData()
                    cookie_first = global_data.get_cookie_first()
                    my_cookie_first_response = requests.get(
                        url=my_url,
                        headers=header_result, cookies=dealrequest.get_cookie(cookie_first))
                    if charsetutils.checkwebsitecharset(
                            my_cookie_first_response.content) is None or charsetutils.checkwebsitecharset(
                        my_cookie_first_response.content) == "":
                        print("my_cookie_first_response为空或者返回包为空")
                        continue
                    if my_origin_response.content == my_empty_response.content:
                        print("存在越权_空cookie")
                        result_data = result_data + " " + "存在越权_空cookie"
                    else:
                        print("不存在越权_空cookie")

                    if my_origin_response.content == my_cookie_first_response.content:
                        print("存在越权_cookie_first")
                        result_data = result_data + " " + "存在越权_cookie_first"

                    # test_request_response.append(my_request_data)
                    if result_data != "" and result_data is not None and result_data != " ":
                        mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                            judge_out_of_access_flag, my_temp_id, my_time,
                                                            my_request_data,
                                                            my_origin_response_coded,
                                                            my_temp_method, result_data)
                        test_request_response_dict[my_request_data] = result_data

                else:
                    continue
            else:
                if global_data.origin_userid in str(url_path_parama):
                    print("user id 在request get data里面")
                    if is_only_onestring(str(url_path_parama), global_data.origin_userid):
                        mypayloadlist = [
                            str(url_path_parama).replace(global_data.origin_userid, global_data.userid_first)]
                        mypayloadlist2 = [
                            str(url_path_parama).replace(global_data.origin_userid, global_data.userid_second)]
                    else:
                        mypayloadlist = makepayloadstring.makereplacestring(str(url_path_parama),
                                                                            global_data.userid_first,
                                                                            my_temp_method,
                                                                            "normal", global_data.origin_userid)

                        mypayloadlist2 = makepayloadstring.makereplacestring(str(url_path_parama),
                                                                             global_data.userid_second,
                                                                             my_temp_method,
                                                                             "normal", global_data.origin_userid)
                    counter = 0
                    for payloadline in mypayloadlist:
                        try:
                            add_replace_my_url = str(
                                my_httptype) + "://" + request_url_host + url_path_string + "?" + payloadline
                            my_replaceid_response = requests.get(url=add_replace_my_url, headers=header_result,
                                                                 cookies=request_dict_cookie, timeout=(3, 7))
                        except Exception as e:
                            print(e)
                            add_replace_my_url = None

                        try:
                            add_replace_my_url2 = str(my_httptype) + "://" + request_url_host + url_path_string + "?" + \
                                                  mypayloadlist2[counter]
                            my_replaceid_response2 = requests.get(url=add_replace_my_url2, headers=header_result,
                                                                  cookies=request_dict_cookie, timeout=(3, 7))
                        except Exception as e:
                            print(e)
                            add_replace_my_url2 = None
                        print("替换uid后返回值")
                        # print(add_replace_my_url)
                        # print(my_replaceid_response.content.decode("utf-8"))
                        if mydealexpvul.dealexpoutofaccess(
                                my_replaceid_response.content.decode("utf-8")) or mydealexpvul.dealexpoutofaccess(
                            my_replaceid_response2.content.decode("utf-8")):
                            print("权限无效等")
                            # print(my_origin_response.content.decode("utf-8"))
                            # print(my_replaceid_response.content.decode("utf-8"))
                            continue
                        if json_no_timestamp(my_origin_response_coded, global_data.origin_userid) != json_no_timestamp(
                                charsetutils.checkwebsitecharset(my_replaceid_response.content),
                                global_data.userid_first):
                            if json_no_timestamp(charsetutils.checkwebsitecharset(my_replaceid_response2.content),
                                                 global_data.userid_second) != json_no_timestamp(
                                charsetutils.checkwebsitecharset(my_replaceid_response.content),
                                global_data.userid_first):
                                print("存在越权_userid " + global_data.userid_first)
                                result_data = "存在越权_userid " + global_data.userid_first
                                if result_data != "" and result_data is not None and result_data != " ":
                                    mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                        judge_out_of_access_flag,
                                                                        my_temp_id,
                                                                        my_time,
                                                                        my_request_data,
                                                                        my_origin_response_coded,
                                                                        my_temp_method, result_data)
                                    test_request_response_dict[my_request_data] = result_data
                        counter = counter + 1
                else:
                    print("user id 不在request post data里面")
                print(my_origin_response.content)
                if my_origin_response_coded is None or my_origin_response_coded == "" or request_dict_cookie == {}:
                    # str(origin_response.decode())
                    print("cookie为空或者返回包为空")
                    continue

                my_empty_response = requests.get(
                    url=my_url,
                    headers=header_result, cookies="")
                print("response empty")

                if charsetutils.checkwebsitecharset(
                        my_empty_response.content) is None or charsetutils.checkwebsitecharset(
                    my_empty_response.content) == "":
                    print("my_empty_response为空或者返回包为空")
                    continue
                # print(my_empty_response.content.decode())

                # global_data = myData()
                cookie_first = global_data.get_cookie_first()
                my_cookie_first_response = requests.get(
                    url=my_url,
                    headers=header_result, cookies=dealrequest.get_cookie(cookie_first))
                if charsetutils.checkwebsitecharset(
                        my_cookie_first_response.content) is None or charsetutils.checkwebsitecharset(
                    my_cookie_first_response.content) == "":
                    print("my_cookie_first_response为空或者返回包为空")
                    continue
                if my_origin_response.content == my_empty_response.content:
                    print("存在越权_空cookie")
                    result_data = result_data + " " + "存在越权_空cookie"
                else:
                    print("不存在越权_空cookie")

                if my_origin_response.content == my_cookie_first_response.content:
                    print("存在越权_cookie_first")
                    result_data = result_data + " " + "存在越权_cookie_first"

                # test_request_response.append(my_request_data)
                if result_data != "" and result_data is not None and result_data != " ":
                    mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type, judge_out_of_access_flag,
                                                        my_temp_id, my_time,
                                                        my_request_data,
                                                        my_origin_response_coded,
                                                        my_temp_method, result_data)
                    test_request_response_dict[my_request_data] = result_data
        elif my_temp_method == "DEFAULT":
            continue

    print("存在漏洞数量")
    Vulnerabilitynumber = len(test_request_response_dict.keys())
    print(Vulnerabilitynumber)


class XssPlatform:
    my_flag = "xss"


def payloadlist_xss(basepayloadlist, requestdict):
    print("start new xss fuzz")
    for baselist in basepayloadlist:
        print(baselist)
    print("start 插入payload")
    my_xssplatform = XssPlatform()
    print("xss" + requestdict)
    total_type = "漏洞"
    details_type = "xss"

    my_request_list = []
    all_my_request_list = mysqlutil.get_most_customers(requestdict)

    print("get data")
    for basepayload_line in basepayloadlist:

        for i in all_my_request_list:
            my_temp_method = i[4]
            my_request_data = i[2]
            my_temp_id = i[0]
            my_time = i[1]
            my_httptype = i[5]
            # 判断重复数据请求包
            if mydealduplicate.dealduplicatemain(str(my_request_data)):
                print("重复数据包")
                continue
            if my_request_data not in my_request_list:
                my_request_list.append(my_request_data)

            split_string = list(my_request_data.split("\r\n"))
            split_string.remove('')
            header_list = split_string[1:]
            contenttypestring = ""  # 判断类型的contenttype
            hoststring = ""  # 判断类型的host
            print("header list")

            for hl in header_list:
                if "Content-Type:" in hl:
                    contenttypestring = hl
                if "Host:" in hl:
                    hoststring = hl
            header_list = "\n".join(header_list)
            if "Content-Type:" not in header_list:
                contenttypestring = header_list
            request_url_host = str(hoststring).replace("Host: ", "")
            request_url_path = str(split_string[0]).replace(my_temp_method + " ", "").replace(" HTTP/1.1", "")
            request_url_path = request_url_path.strip()

            if my_httptype == "http" or my_httptype == "https":
                my_url = my_httptype + "://" + request_url_host + request_url_path
            else:
                print("非http https数据包")
                continue

            # my_url = "http://" + request_url_host + request_url_path
            print(my_url)

            (request_post_data, my_origin_cookie, header_result) = dealrequest.get_headers(header_list, my_temp_method)
            print(my_origin_cookie)
            print("cookie is ")
            print(my_origin_cookie)
            request_dict_cookie = dealrequest.get_cookie(str(my_origin_cookie))
            print(request_dict_cookie)

            print("method")
            print(type(my_temp_method))

            next_list = ["GET /robots.txt HTTP/1.1", "GET / HTTP/1.1", "GET /login.php HTTP/1.1",
                         "GET /admin.php HTTP/1.1"]
            if split_string[0] in next_list:
                print("continue")
                continue
            else:
                print("not none")
                # print("\n".join(header_list))

                print("add payload to request_url_path")
                url_path_string = ""
                url_path_parama = ""
                url_path_payload = request_url_path.split("?")
                print(url_path_payload)
                print(len(url_path_payload))
                if len(url_path_payload) == 2:
                    print(url_path_payload[0])
                    url_path_string = url_path_payload[0]
                    print(url_path_payload[-1])
                    url_path_parama = url_path_payload[-1]
                    print(len(url_path_payload))
                elif len(url_path_payload) == 3:
                    print("参数为3个")
                    url_path_string = str(url_path_payload[0]) + "?" + str(url_path_payload[1])
                    url_path_parama = url_path_payload[-1]
                    print(url_path_string)
                    print(url_path_parama)
                elif len(url_path_payload) == 1:
                    print(type(url_path_payload))
                    url_path_string = "".join(url_path_payload)

            if my_temp_method == "GET":
                print(my_temp_method)
                if len(url_path_payload) < 2:
                    continue
                else:
                    mypayloadlist = makepayloadstring.makepayloadstring(str(url_path_parama), basepayload_line,
                                                                        my_temp_method,
                                                                        "normal")
                    for mypayloadline in mypayloadlist:
                        add_xss_my_url = "http://" + request_url_host + url_path_string + "?" + mypayloadline

                        try:
                            my_xss_response = requests.get(url=add_xss_my_url, headers=header_result,
                                                           cookies=request_dict_cookie)
                        except Exception as e:
                            print(e)
                            continue
                        if my_xss_response.content is None or my_xss_response.status_code == 404:
                            continue
                        # elif basepayload_line in str(my_xss_response.content.decode('utf-8')):

                        elif dealstringencode(str(charsetutils.checkwebsitecharset(my_xss_response.content)),
                                              basepayload_line):
                            # write_vulnerability_to_db()
                            if mydealexpvul.dealexpvulmain(str(my_xss_response.content.decode('utf-8'))):
                                continue
                            print("write into database")
                            mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                my_xssplatform.my_flag, my_temp_id,
                                                                my_time,
                                                                my_request_data,
                                                                my_xss_response.content.decode("utf-8").encode("utf-8"),
                                                                my_temp_method,
                                                                "xss " + str(mypayloadline))

            elif my_temp_method == "POST":
                print("method")
                print(my_temp_method)
                # print("post")
                print(header_list)
                print(type(header_list))

                # if "Accept: application/json, text/plain, */*" in header_list:
                # 判断太粗了
                # contenttypestring
                # if "application/json" in header_list:
                if "application/json" in contenttypestring:
                    print("json格式")
                    print(type(request_post_data))
                    # 调试json 数据
                    print(len(request_post_data))
                    if len(request_post_data) == 0:
                        continue
                    request_post_data_dict = json.loads(request_post_data)
                    print(type(request_post_data_dict))
                    print(request_post_data_dict)
                    # todo json 字典生成多个payload字典
                    # for mypayloadline in mypayloadlist:  # url的参数处理，主要是GET的，POST请求基本不用的
                    print("url处理后的")
                    # print(mypayloadline)
                    # 生成payload   给定请求json、payloadstring,返回字典列表
                    # deal_dict_class
                    json_list = returnjson_payload(request_post_data_dict, str(basepayload_line), "")
                    for my_request_data_temp in json_list:

                        print(type(my_request_data_temp))
                        request_post_data = json.dumps(my_request_data_temp)
                        print(type(request_post_data))
                        print(request_post_data)
                        # 请求
                        print("post数据")
                        print(request_post_data)
                        if request_post_data is None:
                            continue

                        for i in request_post_data_dict:
                            print(i)

                        try:
                            my_origin_response = requests.post(
                                url=my_url,
                                headers=header_result, cookies=request_dict_cookie, json=request_post_data)
                            try:
                                utf8response = my_origin_response.content.decode('utf-8')
                                print(utf8response)
                            except:
                                print("获取返回包异常")
                                utf8response = "response"
                            if my_origin_response.content is None or my_origin_response.status_code == 404:
                                continue
                            elif basepayload_line in utf8response:
                                if mydealexpvul.dealexpvulmain(utf8response):
                                    continue
                                # write_vulnerability_to_db()
                                print("write into database")
                                print(utf8response)
                                mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                    my_xssplatform.my_flag, my_temp_id,
                                                                    my_time,
                                                                    my_request_data,
                                                                    my_origin_response.content.decode("utf-8").encode(
                                                                        "utf-8"),
                                                                    my_temp_method,
                                                                    "xss " + str(my_request_data_temp))
                        except:
                            print("post请求异常")


                elif 'Content-Type: application/x-www-form-urlencoded' in contenttypestring:
                    mypayloadlist = makepayloadstring.makepayloadstring(str(request_post_data), basepayload_line,
                                                                        my_temp_method,
                                                                        "normal")
                    print("常规post格式")
                    print(type(request_post_data))
                    print(request_post_data)
                    # add_xss_my_url = "http://" + request_url_host + url_path_payload[0] + "?" + mypayloadline
                    for mypayloadline in mypayloadlist:
                        print(mypayloadline)

                        # print(request_url_host)
                        # print(url_path_string)
                        # print(mypayloadline)
                        add_xss_my_url = "http://" + request_url_host + url_path_string + "?" + mypayloadline
                        print("add_xss_my_url")
                        print(add_xss_my_url)
                        print(request_dict_cookie)
                        print(json.dumps(request_dict_cookie, ensure_ascii=False))
                        try:
                            my_xss_response = requests.post(
                                url=my_url, data=mypayloadline,
                                headers=header_result,
                                cookies=request_dict_cookie)
                        except Exception as e:
                            print(e)
                            continue
                        print(my_xss_response.content)
                        if my_xss_response.content is None or my_xss_response.status_code == 404:
                            continue
                        # elif basepayload_line in str(my_xss_response.content.decode('utf-8')):

                        elif dealstringencode(str(charsetutils.checkwebsitecharset(my_xss_response.content)),
                                              basepayload_line):
                            # write_vulnerability_to_db()
                            if mydealexpvul.dealexpvulmain(str(my_xss_response.content.decode('utf-8'))):
                                continue
                            print("write into database")
                            print(my_xss_response.content.decode('utf-8'))
                            mysqlutil.write_vulnerability_to_db(requestdict, total_type, details_type,
                                                                my_xssplatform.my_flag, my_temp_id,
                                                                my_time,
                                                                my_request_data,
                                                                my_xss_response.content.decode("utf-8").encode("utf-8"),
                                                                my_temp_method,
                                                                "xss " + str(mypayloadline))
