from urllib.parse import quote
import time


def makepayloadstring(requeststring, payloadstr, requestmethod, requestform):
    if requestmethod == "GET" or (requestmethod == "POST" and requestform == "normal"):
        url_path_payload_str = requeststring.split("&")
        print(url_path_payload_str)
        temp_url_path = ""
        result_list = []  # 结果列表
        temp_url_path_list = []
        total_count = 0
        print("len(url_path_payload_str)")
        print(len(url_path_payload_str))
        if len(url_path_payload_str) == 1 and "=" in requeststring:  # /post   ?/a=dfsdf
            result_list.append(requeststring + payloadstr)
            print(requeststring + payloadstr)
            return result_list
        if len(url_path_payload_str) == 1 and ("=" not in requeststring):  # /post   ?/a=dfsdf
            result_list.append(requeststring)
            print("请求url没有带具体参数的")
            print(requeststring)
            return result_list
        else:
            for url_path_line in url_path_payload_str:
                temp_before_string = ""
                temp_after_string = ""
                if total_count == 0:
                    temp_before_string = ""
                    # "&".join(temp_url_path_list)
                    print(total_count)
                    temp_after_string = "&".join(url_path_payload_str[total_count + 1:])
                    print("最后的")
                    print(temp_after_string)
                    temp_result = str(url_path_line) + payloadstr + "&" + temp_after_string
                    if temp_result not in result_list:
                        result_list.append(temp_result)
                elif total_count == len(url_path_payload_str) - 1:
                    temp_before_string = ""
                    # "&".join(temp_url_path_list)
                    print("最后的一个")
                    print(total_count)
                    temp_before_string = "&".join(url_path_payload_str[:total_count])
                    print("最前的")
                    print(temp_before_string)
                    temp_result = temp_before_string + "&" + str(url_path_line) + payloadstr
                    if temp_result not in result_list:
                        result_list.append(temp_result)
                else:
                    print(total_count)
                    temp_before_string = "&".join(url_path_payload_str[:total_count])
                    temp_after_string = "&".join(url_path_payload_str[total_count + 1:])
                    print(temp_before_string)
                    print(url_path_payload_str[total_count])
                    print(temp_after_string)
                    temp_result = str(temp_before_string) + "&" + str(url_path_line) + payloadstr + "&" + str(
                        temp_after_string)
                    if temp_result not in result_list:
                        result_list.append(temp_result)
                total_count = total_count + 1
            return result_list
    else:
        print("other type make")


# rewrite  get 伪静态
# string 180052 get normal/...  200010
# /chatserver/app/api/user/180052
# /chatserver/app/api/user/fsdf.html
# /chatserver/app/api/user/fsdf.action ...
def makerewritestring(requeststring, payloadstr, requestmethod, requestform, toreplacestring):
    if requestmethod == "GET":
        url_path_payload_str = requeststring.split("/")
        print(url_path_payload_str)
        temp_url_path = ""
        result_list = []  # 结果列表
        counter = 0
        beforestring = ""
        afterstring = ""

        for line in url_path_payload_str:
            templist = []
            wholestring = ""
            if line == toreplacestring:
                print(len(toreplacestring))
                print(counter)
                if counter == 0:
                    beforestring = ""
                    afterstring = "/".join(url_path_payload_str[1:])
                    print(afterstring)
                    # print(url_path_payload_str[])
                elif counter == len(url_path_payload_str) - 1:
                    beforestring = "/".join(url_path_payload_str[:-1])
                    afterstring = ""
                    print(beforestring)
                else:
                    beforestring = "/".join(url_path_payload_str[:counter])
                    afterstring = "/".join(url_path_payload_str[counter + 1:])
                    print(beforestring)
                    print(afterstring)

                if str(beforestring) != "":
                    templist.append(str(beforestring))
                templist.append(str(payloadstr))
                if str(afterstring) != "":
                    templist.append(str(afterstring))

                wholestring = "/".join(templist)
                if wholestring not in result_list:
                    result_list.append(wholestring)
            counter = counter + 1
        return result_list
    else:
        print("other type make")
        return None


# toreplacestring 待替换的字符串
def makereplacestring(requeststring, payloadstr, requestmethod, requestform, toreplacestring):
    if requestmethod == "GET" or (requestmethod == "POST" and requestform == "normal"):
        url_path_payload_str = requeststring.split("&")
        print(url_path_payload_str)
        temp_url_path = ""
        result_list = []  # 结果列表
        temp_url_path_list = []
        total_count = 0
        print("len(url_path_payload_str)")
        print(len(url_path_payload_str))
        if len(url_path_payload_str) == 1 and "=" in requeststring:  # /post   ?/a=dfsdf
            url_path_payload_str_one = url_path_payload_str[0].split("=")
            tempresult = url_path_payload_str_one[0] + "=" + payloadstr
            result_list.append(tempresult)
            return result_list
        if len(url_path_payload_str) == 1 and ("=" not in requeststring):  # /post   ?/a=dfsdf
            result_list.append(requeststring)
            print("请求url没有带具体参数的")
            print(requeststring)
            return result_list
        else:
            for url_path_line in url_path_payload_str:
                temp_before_string = ""
                temp_after_string = ""
                if total_count == 0:
                    temp_before_string = ""
                    # "&".join(temp_url_path_list)
                    print(total_count)
                    temp_after_string = "&".join(url_path_payload_str[total_count + 1:])
                    print("最后的")
                    print(temp_after_string)
                    print("str(url_path_line")
                    print(str(url_path_line))
                    temp_replace_str = url_path_line.split('=')
                    print(temp_replace_str[0])
                    if temp_replace_str[1] == toreplacestring:
                        temp_replace_str[1] = payloadstr
                        print(temp_replace_str[1])

                        temppayloadstring = '='.join(temp_replace_str)

                        temp_result = temppayloadstring + "&" + temp_after_string
                        if temp_result not in result_list:
                            result_list.append(temp_result)
                    else:
                        print("not userid ")
                elif total_count == len(url_path_payload_str) - 1:
                    temp_before_string = ""
                    # "&".join(temp_url_path_list)
                    print("最后的一个")
                    print(total_count)
                    temp_before_string = "&".join(url_path_payload_str[:total_count])
                    print("最前的")
                    print(temp_before_string)

                    temp_replace_str = url_path_line.split('=')
                    print(temp_replace_str[0])
                    if temp_replace_str[1] == toreplacestring:
                        temp_replace_str[1] = payloadstr
                        print(temp_replace_str[1])

                        temppayloadstring = '='.join(temp_replace_str)

                        temp_result = temp_before_string + "&" + temppayloadstring
                        if temp_result not in result_list:
                            result_list.append(temp_result)
                    else:
                        print("not userid ")
                else:
                    print(total_count)
                    temp_before_string = "&".join(url_path_payload_str[:total_count])
                    temp_after_string = "&".join(url_path_payload_str[total_count + 1:])
                    print(temp_before_string)
                    print(url_path_payload_str[total_count])
                    print(temp_after_string)

                    temp_replace_str = url_path_line.split('=')
                    print(temp_replace_str[0])

                    if temp_replace_str[1] == toreplacestring:
                        temp_replace_str[1] = payloadstr
                        print(temp_replace_str[1])
                        temppayloadstring = '='.join(temp_replace_str)
                        temp_result = str(temp_before_string) + "&" + temppayloadstring + "&" + str(
                            temp_after_string)
                        if temp_result not in result_list:
                            result_list.append(temp_result)
                    else:
                        print("not userid ")
                total_count = total_count + 1
            return result_list
    else:
        print("other type make")


def get_value_from_json(my_flag, key, tdict, tem_list, my_number_count):
    """
    从Json中获取key值，
    :param key:
    :param tdict:
    :param tem_list:
    :return:
    """
    global tempstring_value
    if not isinstance(tdict, dict):
        return tdict + "is not dict"
    else:
        for key_line in tdict.keys():
            if isinstance(tdict[key_line], dict):
                get_value_from_json(my_flag, key, tdict[key_line], tem_list, my_number_count)
            elif isinstance(tdict[key_line], (list, tuple)):
                tempstring_value = tempstring_value + "-" + str(key_line)
                _get_value(my_flag, key, tdict[key_line], tem_list, my_number_count)
            else:
                # 最终嵌套字典末端
                print(key_line)
                my_number_count = my_number_count + 1
                print(my_number_count)
                # print(tdict[key_line])
                tempstring_value = tempstring_value + "-" + str(key_line)
                # tempstring_value
                if my_flag == "bianli":
                    print(tdict[key_line])
                    tem_list.append(tempstring_value)
                elif my_flag == "replace":
                    print("replace")
                    print("当前需要替换的值")
                    print(key)
                    print("当前tempstring_value")
                    print(tempstring_value)
                    if key == tempstring_value:
                        print("开始替换ing")
                        tdict[key_line] = tdict[key_line] + str(" xss")
                        print("替换之后的值")
                        print(tdict[key_line])
                        return tdict
                    else:
                        print("不用替换")
    if my_flag == "bianli":
        return tem_list
    elif my_flag == "replace":
        return tdict


def _get_value(my_flag, key, tdict, tem_list, my_number_count):
    """

    :param key:
    :param tdict:
    :param tem_list:
    :return:
    """
    for value in tdict:
        if isinstance(value, (list, tuple)):
            my_number_count = my_number_count + 1
            _get_value(my_flag, tdict, my_number_count)
        elif isinstance(value, dict):
            get_value_from_json(my_flag, key, value, tem_list, my_number_count)


resultdata = []
test_dic = {
    "广州": [
        {
            "从化": [
                {
                    "影院": "从化从艺流溪影剧院",
                    "地址": "从化市新城东路新世纪广百三楼",
                    "电话": "020-87936828"
                }
            ],
            "萝岗": [
                {
                    "影院": "万达国际影城-萝岗店",
                    "地址": "广州市萝岗区科丰路89号万达广场娱乐楼4层万达影城",
                    "电话": "020-29097668"
                }
            ]
        }
    ],
    "韶关": [
        {
            "乳源": [
                {
                    "影院": "乳源瑶族自治县云河电影城",
                    "地址": "广东省韶关市乳源县政府广场广客隆4楼金逸影城",
                    "电话": "0751-5368366"
                }
            ],
            "武江": [
                {
                    "影院": "大地影院-韶关中环广场",
                    "地址": "韶关市武江区惠民南路50号中环广场5楼",
                    "电话": "0751-8529508"
                }
            ]
        }
    ],
    "深圳": [
        {
            "观澜": [
                {
                    "影院": "金逸国际影城-深圳观澜店",
                    "地址": "深圳市观澜镇观光路万悦城广场4楼（富士康南门）",
                    "电话": "0755-88370290"
                }
            ],
            "盐田": [
                {
                    "影院": "冷杉欢腾影城（深圳店）",
                    "地址": "深圳市盐田区沙头角瀚海江岸荣津乐活城4楼",
                    "电话": "0755-25770793"
                }
            ]
        }
    ]
}

# temp_list = makereplacestring("ab=45&cd=6737005020266300&ef=87", "3014395689924638", "POST", "normal","6737005020266300")
# print("result")
# for f in temp_list:
#     print(f)

# tempstring_value = ""
# allGuests = {'Alice': {'apples': 5, 'pretzels': {'12': {'beijing': 456}}},
#              'Bob': {'ham sandwiches': 3, 'apple': 2},
#              'Carol': {'cups': 3, 'apple pies': 1}}
# number_count = 0
# my_result_list = get_value_from_json("bianli", "从化", test_dic, resultdata, number_count)
# print("获取数据")
# for fsdf in my_result_list:  # 遍历处理
#     print(fsdf)
#
# print("开始替换")
# # 初始化 tempstring_value
# tempstring_value = ""
# temp_list = []
# for fsdf in my_result_list:  # 遍历处理
#     temp_list.append(get_value_from_json("replace", fsdf, test_dic, resultdata, number_count))
#     time.sleep(0.2)
#     tempstring_value = ""
#
# # 初始化 tempstring_value
# # tempstring_value = ""
# print("result")
# print(len(temp_list))
# for fsdfsg in temp_list:
#     print(fsdfsg)
# for fsdf in temp_list:
#     print(type(fsdf))
#     print(fsdf)
#     fsdf = get_value_from_json("bianli", "", fsdf, resultdata, number_count)
#     tempstring_value = ""

# # templist = ["0", "1", "2", "3", "4", "5", "6", "7"]
# # tempstring = "".join(templist)
# # testlist(str(tempstring))
# print(replace_k(allGuests))
# print("key list")
# tempresult_list = []
# # print(get_dict_key(allGuests,tempresult_list))
# print(makerewritestring("chatserver/app/api/user/170448","200357", "GET", "normal", "170448"))
