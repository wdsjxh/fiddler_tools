import time
import sys
sys.path.append("../")
from utils.mysqlutils import mysqlutil
from utils.deal_dict_class import return_json_look_up
from utils.dealrequest import dealrequest
import json
import logging
from utils.encryutils import encryutils

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("fiddler_tools.log", encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Base_judge_out_of_access:
    def __init__(self):
        self.requestdict = {}
        self.mysqlutil = mysqlutil()

    def run(self, requestdict):
        print("统计所有分词数据字典")
        my_json_list = self.mysqlutil.get_request_json({})
        print(len(my_json_list))
        segment_dict = {}
        for json_line in my_json_list:
            print(json_line)
            try:
                json_line = json_line.replace("'", '"')
                dict_line = json.loads(json_line)
            except Exception as e:
                print("异常")
                print(e)
                continue
            print(type(dict_line))
            print(dict_line)
            if not dict_line:
                print("跳过")
                continue
            else:
                for key, value in dict_line.items():
                    if key == "" or key is None or value == "" or value is None:
                        continue
                    if key not in segment_dict.keys():
                        print("新的键值" + key)
                        segment_dict[key] = value
                    else:
                        print("原来的添加")
                        # if segment_dict[key] not list:
                        if not isinstance(segment_dict[key], list):
                            if not value == segment_dict[key]:
                                temp_list = [segment_dict[key], value]
                                segment_dict[key] = temp_list
                        elif value not in segment_dict[key]:
                            list(segment_dict[key]).append(value)
        print('segment_dict')
        print(segment_dict)
        # 数据包
        my_request_list = self.mysqlutil.get_most_customers(requestdict)
        print(len(my_request_list))
        for line in my_request_list:
            my_temp_method = line["method"]
            my_request_data = line["request"]
            my_response_data = line["response"]
            my_temp_id = line["id"]
            my_time = line["time"]
            my_httptype = line["httptype"]



        # 判断数据包
        # 替换id扩展
        # id=12&uid=45&lalada=23ffd
        # for line in 每个存在的参数列表  每个有 多个值  {id:[1,3,5],uid:[3,5,7]}  之前判断存在
        # 外层两个for循环  返回响应包
        # {"id":{"origin_id":"1","replace_id":[23,45,67,87]}
        # {"uid":{"origin_uid":"1","replace_uid":[23,45,67,87]}


my_base = Base_judge_out_of_access()
my_base.run({'username': 'admin', 'project': '天天基金'})
