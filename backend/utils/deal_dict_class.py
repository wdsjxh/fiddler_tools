# coding:utf8
import copy
import json
import time
from utils.timeutils import istimestamp
from utils.timeutils import isdatetimestring
from utils.timeutils import isexpstring
from utils.check_sensitive import run

# 初始化 tempstring_value
tempstring_value = ""


class car:
    '''interface as Product'''

    def drive(self):
        pass

    def drivereplace(self):
        pass


class Get_value_from_json(car):
    '''Concrete Product'''
    global_dict = {}
    global_list = []
    look_up_dict = {}  # 遍历参数和值
    _my_flag = ""
    _key = ""
    result_dict = {}  # 敏感信息检测结果字典  {"身份证":[],"银行卡”：[]}
    target_list = []  # 去重列表

    # add
    toreplace = ""

    def __init__(self, my_flag, key, myjson, tem_list, my_number_count, xss_payload, toreplace):
        # self.__name = carname
        self._my_flag = my_flag
        self._key = key
        self._myjson = myjson
        self._tem_list = tem_list
        self._my_number_count = my_number_count
        self._xss_payload = xss_payload
        self.toreplace = toreplace
        self.result_dict = {}
        self.target_list = []
        self.look_up_dict = {}

    def drive(self, _my_flag, _key, _myjson, _tem_list, _my_number_count, _xss_payload, _emptystring):
        # def drive(self, my_flag, key, myjson, tem_list, my_number_count):
        # mydata = myData()
        my_flag = _my_flag
        key = _key
        myjson = _myjson
        tem_list = _tem_list
        my_number_count = _my_number_count
        my_xss_payload = _xss_payload
        tdict = myjson

        global tempstring_value
        if not isinstance(tdict, dict):
            return tdict + "is not dict"
        else:
            for key_line in tdict.keys():
                if isinstance(tdict[key_line], dict):
                    self.look_up_dict[key_line] = "dict"
                    self.drive(my_flag, key, tdict[key_line], tem_list, my_number_count, my_xss_payload, _emptystring)
                else:
                    my_number_count = my_number_count + 1
                    tempstring_value = tempstring_value + "-" + str(key_line)
                    if my_flag == "bianli":
                        if _xss_payload == "look_up":
                            try:
                                if tdict[key_line] is None:
                                    print("tdict [key_line] is None")
                                else:
                                    self.look_up_dict[key_line] = tdict[key_line]
                            except Exception as e:
                                print(e)
                        else:
                            tem_list.append(tempstring_value)
                    elif my_flag == "replace":

                        if key == tempstring_value:

                            tdict[key_line] = str(tdict[key_line]) + _xss_payload
                        else:
                            print("不用替换")
        if my_flag == "bianli":
            if _xss_payload == "look_up":
                return self.look_up_dict
            self.global_list = tem_list
            return tem_list
        elif my_flag == "replace":
            self.global_dict = tdict
            return tdict

    # 替换掉原来的值{'荔湾': 'fdfxss'} => {'荔湾': 'xss'}
    def drivereplace(self, _my_flag, _key, _myjson, _tem_list, _my_number_count, _xss_payload, toreplace):
        # def drive(self, my_flag, key, myjson, tem_list, my_number_count):
        # mydata = myData()
        my_flag = _my_flag
        key = _key
        myjson = _myjson
        tem_list = _tem_list
        my_number_count = _my_number_count
        my_xss_payload = _xss_payload
        tdict = myjson
        global tempstring_value
        if not isinstance(tdict, dict):
            return tdict + "is not dict"
        else:
            for key_line in tdict.keys():
                if isinstance(tdict[key_line], dict):
                    self.drivereplace(my_flag, key, tdict[key_line], tem_list, my_number_count, my_xss_payload,
                                      toreplace)
                else:
                    my_number_count = my_number_count + 1
                    tempstring_value = tempstring_value + "-" + str(key_line)
                    if my_flag == "bianli":
                        tem_list.append(tempstring_value)
                    elif my_flag == "replace":
                        my_value = tdict[key_line]
                        if _xss_payload == "check_sensitive_info":
                            if not isinstance(my_value, list):
                                if my_value not in self.target_list:
                                    self.target_list.append(my_value)
                                    temp_result = run(my_value)
                                    if temp_result:
                                        self.result_dict[my_value] = temp_result  # 直接字典

                        # {'bank_card': 1, 'id_card': 1}
                        elif _xss_payload == "timestamp":
                            tdict[key_line] = str(tdict[key_line]).strip()
                            #  判断10or13位纯数字，是否一周内时间戳   或者任意时间字符串  或者指定字符串  或者等于uid
                            if istimestamp(str(tdict[key_line])) or isdatetimestring(
                                    str(tdict[key_line])) or isexpstring(str(tdict[key_line])) or toreplace == str(
                                tdict[key_line]):
                                tdict[key_line] = _xss_payload
                        elif key == tempstring_value and tdict[key_line] == toreplace:
                            # 继续判断是否是需要替换的字符串
                            tdict[key_line] = _xss_payload
                        else:
                            print("不用替换")

        if my_flag == "bianli":
            self.global_list = tem_list
            return tem_list
        elif my_flag == "replace":
            if _xss_payload == "check_sensitive_info":
                # self.result_dict.clear()
                # self.target_list.clear()
                return self.result_dict

            self.global_dict = tdict
            return tdict


class Benz(car):
    '''Concrete Product'''

    def __init__(self, carname):
        self.__name = carname

    def drive(self):
        print("Drive the Benz as " + self.__name)


class driver:
    '''Factory also called Creator'''

    def driverCar(self):
        return car()


class Benzdriver(driver):
    '''Concrete Creator'''

    def driverCar(self):
        return Benz("Benz")


class Get_value_from_jsondriver(driver):
    def driverCar(self):
        return Benz("Benz car driver")

    def driverget_value_json_from(self, my_flag, key, myjson, tem_list, my_number_count, xss_payload, emptystring):
        return Get_value_from_json(my_flag, key, myjson, tem_list, my_number_count, xss_payload, emptystring)

    # 待替换字符串
    def driverget_value_json_replace(self, my_flag, key, myjson, tem_list, my_number_count, xss_payload, toreplace):
        return Get_value_from_json(my_flag, key, myjson, tem_list, my_number_count, xss_payload, toreplace)


def returnjson_payload(jsonstring, payloadstring, emptystring):
    area = jsonstring

    resultdata = []
    number_count = 0

    # false null 等会报错
    # myDict = eval(myStr)

    dirver = Get_value_from_jsondriver()
    car = dirver.driverget_value_json_from("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                                           emptystring)
    my_result_list = car.drive("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                               emptystring)

    print("获取数据")
    multi_dict_dict = {}  # 为了避免全局变量修改
    for fsdf in my_result_list:  # 遍历处理

        multi_dict_dict[fsdf] = area

    print("开始替换")

    temp_list = []
    global tempstring_value
    tempstring_value = ""
    for fsdf in my_result_list:  # 遍历处理
        resultdata1 = []
        print("当前key")
        print(fsdf)
        # temp_result_dict = get_value_from_json("replace", fsdf, json.dumps(area), resultdata1, number_count)
        # temp_result_dict = get_value_from_json("replace", fsdf, json.dumps(area), resultdata1, number_count)
        dirver = Get_value_from_jsondriver()
        car = dirver.driverget_value_json_from("replace", fsdf, copy.deepcopy(area), resultdata1, number_count,
                                               payloadstring, emptystring)
        temp_result_dict = car.drive("replace", fsdf, copy.deepcopy(area), resultdata1, number_count, payloadstring,
                                     emptystring)
        temp_list.append(temp_result_dict)

        # time.sleep(0.2)
        tempstring_value = ""

    # 初始化 tempstring_value
    tempstring_value = ""
    print("result")
    print(len(temp_list))
    return temp_list


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        # print(e)
        return False
    return True


# 遍历
# payloadstring=="timestamp"时，toreplacestring传入uid，排除掉返回包里面的
# payloadstring=="look_up"时，toreplacestring传入uid，排除掉返回包里面的
# toreplacestring 判断替换的字符串比如uid
def return_json_look_up(jsonstring, payloadstring, toreplacestring):
    area = jsonstring
    resultdata = []
    my_result_dict = {}
    number_count = 0

    dirver = Get_value_from_jsondriver()
    emptystring = ""
    car = dirver.driverget_value_json_from("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                                           emptystring)
    my_result_dict = car.drive("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                               emptystring)
    return my_result_dict


# 替换掉原来的值{'荔湾': 'fdfxss'} => {'荔湾': 'xss'}
# payloadstring=="timestamp"时，toreplacestring传入uid，排除掉返回包里面的
# toreplacestring 判断替换的字符串比如uid
def returnreplacejson_payload(jsonstring, payloadstring, toreplacestring):
    area = jsonstring
    resultdata = []
    number_count = 0
    xss_payload = "xss"

    print("字典字符串转化")

    myStr = str(area)

    # myDict = eval(myStr)

    dirver = Get_value_from_jsondriver()
    emptystring = ""
    car = dirver.driverget_value_json_from("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                                           emptystring)
    my_result_list = car.drive("bianli", "从化", copy.deepcopy(area), resultdata, number_count, payloadstring,
                               emptystring)
    print("global data")
    print(car.global_list)

    print("获取数据")
    multi_dict_dict = {}  # 为了避免全局变量修改
    for fsdf in my_result_list:  # 遍历处理
        multi_dict_dict[fsdf] = area

    print("开始替换")

    temp_list = []
    global tempstring_value
    tempstring_value = ""
    for fsdf in my_result_list:  # 遍历处理
        resultdata1 = []
        print("当前key")
        print(fsdf)
        # 传另外的判断参数
        dirver = Get_value_from_jsondriver()
        car = dirver.driverget_value_json_replace("replace", fsdf, copy.deepcopy(area), resultdata1, number_count,
                                                  payloadstring, toreplacestring)
        temp_result_dict = car.drivereplace("replace", fsdf, copy.deepcopy(area), resultdata1, number_count,
                                            payloadstring, toreplacestring)
        # 排除自己
        if temp_result_dict != jsonstring and temp_result_dict not in temp_list:  # payloadstring == timestamp情况
            temp_list.append(temp_result_dict)
        # time.sleep(0.2)
        tempstring_value = ""

    # 初始化 tempstring_value
    tempstring_value = ""
    print("result")
    print(len(temp_list))
    return temp_list
    # for fsdfsg in temp_list:
    #     print(fsdfsg)


# if __name__ == "__main__":
#     area = {
#         '世界': {
#             '中国': {
#                 '广东': {
#                     '佛山': {
#                         '南海': {
#                             '桂城': 0
#                         }
#                     },
#                     '广州': {
#                         '荔湾': 'true'
#                     }
#                 },
#                 '香港': {
#                     '九龙': 1595905002
#                 }
#             },
#             '美国': {'fsdf': 'fsdf'}
#         }
#     }
#     response_content = {
#         'atoken': 'RLtT0F7GbJmmEUeflZ95L/m0n2mnz28FCjXNHIl2SJz95vxrROzcD8uCgMLAQaWoUDuShK0OtTBRANrv46SK7v/euUGT7nlcagGh7FqsHyaM+hIRPI1Fym3DQmVorQAx6YxnXuOhxf2ClubRR2q2oVmK6sFhkF6BAjko3LoddSTCnweqF9I1P/EBdP8Z0Bz1l6frMRpQ/v4ZO72VdWA1Ot5ez2thMSB22PDzfCtk5RSuQmpge2W1OBzHMd2prgNW1Lc1oidI/ueTLGvcosBY8m9ki/FQ+JE1fqMUxra5a2xrzS1Pu5iaaERgd/8ImL+PyYSmIKoFK6Z8YuCnSiKkO1M3k5tAfIfoScQZoYDC7zRgcCZ9FbgwcHxbU6HGF/YZV9KXZUqDny7oAmOBpJQD6EvI57w3Cqc5U7HqA3RSw6gqqz+3ssSd+Hojvjr+DUA1PHLNRPm6',
#         'fsdf': 'wr'}
# response_content = {"result": "fsd", "returnCode": "fsdf", "message": "fsdf", "fsdf": "fsdf",
#                     "dicttest": {"data1": "fasdftg"}}
#
# response_content1 = {"tst": "fsdfg"}
# response_content1 = {"result": 1, "message": "",
#                      "data": {"GameId": "000001", "Name": "基金模拟大赛", "Description": "基金模拟大赛第一赛季",
#                               "BeginDate": "2016-04-01T00:00:00", "EndDate": "2099-12-01T00:00:00",
#                               "Rule": "<p>一、 比赛规则000 </p><p>1. 自行下载安装炒股软件，并进行注册登录。统一用学号注册模拟股市，详细请看首届“知行杯”模拟股票交易大赛注册流程指导。 </p><p>2. 比赛日开始后登录炒股软件，进行网上交易。每名参赛者将获得虚拟人民币50万元用于模拟交易。 </p><p>3. 比赛的股票买卖与实盘股票交易一致。但买卖下单时要注意以下事项： （1）交易时间为正常股市时间：上午9：30-11：30，下午1：00-3：00。买卖与成交与证交所实时情况同步。 </p><p>4.模拟比赛中，国内交易品种只能是在上海、深圳证券交易所上市的A股股票，其它交易品种及新股申购无效。 </p><p>5.参赛者需通过技术支持所提供的炒股软件交易方式进行买卖。委托方式为当日有效的限价委托。 </p><p>6.股票买卖的具体规则同证券交易所公布的证券交易规定基本一致。 （5）发出买卖指令后，交易所涉及的资金或股票，会在交易账户中暂时冻结，直至本笔交易成交或者撤单。 </p><p>7.交易费用与交易所设置相同，股票的交易佣金全部按0.2%扣除，印花税按0.1%扣除。</p>",
#                               "NumberOfPeople": 138368, "MaxPortfolioCount": 5, "MinDisplayPopulationScale": 1000},
#                      "count": 0, "totalCount": 0, "time": "1596518874", "errorcode": "null"}
#
# print(return_json_look_up(response_content, "look_up", "fsdfesdf"))
# print(return_json_look_up(response_content1, "look_up", "fsdfsrerdf"))
# # result_list = returnjson_payload(area, "xss")
# result_dict = returnreplacejson_payload(response_content, "check_sensitive_info", "3d2edaef0e3f4486b322f1119e633c02")
# print(result_dict)
# print(result_list)
# # result_list = returnjson_payload(area, "xss","")
# # print(result_list)
# print(type(result_list))
# print(result_list[0])
# # for i in result_list:
# #     print(type(i))
# #     print(i)
