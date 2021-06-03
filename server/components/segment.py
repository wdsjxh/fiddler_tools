import time
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


class Segment:
    def __init__(self):
        self.requestdict = {}
        self.responsedict = {}
        self.mysqlutil = mysqlutil()
        self.dealrequest = dealrequest()
        self.encryutils = encryutils()
        self.check_result = {}
        self.tempresult = {}
        self.result_data = ""
        self.req_param = ""  # 请求参数
        self.uniq_request = ""

    # 调用替换json字典
    # json返回包替换时间戳 返回字典
    def json_segment_monitor(self, jsonstring, uidstring):
        result_dict = {}
        if not jsonstring:
            return None
        try:
            dict_json = json.loads(jsonstring)
        except Exception as e:
            print(e)
            return {}

        self.tempresult = return_json_look_up(
            dict_json, "look_up",
            uidstring)
        if self.tempresult:
            result_dict = self.tempresult
        return result_dict

    def run(self, my_requestdict):
        my_request_list = self.mysqlutil.get_most_customers(my_requestdict)
        for line in my_request_list:

            my_temp_method = line["method"]
            my_request_data = line["request"]
            my_response_data = line["response"]
            my_temp_id = line["id"]
            my_time = line["time"]
            my_httptype = line["httptype"]

            request_url_host, request_url_path, header_list, contenttypestring = self.dealrequest.get_host_uri_header_type(
                my_request_data, my_temp_method)

            (request_post_data, my_origin_cookie, header_result) = self.dealrequest.get_headers(header_list,
                                                                                                my_temp_method)
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
            self.responsedict = self.json_segment_monitor(my_response_data, "fsaadfsf435456")
            print(self.responsedict)
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
                    self.requestdict = self.dealrequest.url_data_to_dict(request_post_data)
                    self.req_param = "&".join(self.requestdict.keys())
                elif 'application/json' in contenttypestring:
                    print("准备遍历json")
                    print(request_post_data)
                    self.requestdict = self.json_segment_monitor(request_post_data, "fsaadfsf435456")
                    print(self.responsedict)
                    self.req_param = "&".join(self.requestdict.keys())
            elif my_temp_method == "GET":
                self.requestdict = self.dealrequest.url_data_to_dict(url_path_parama)
                self.req_param = "&".join(self.requestdict.keys())
            # http  get  host  uri 参数
            self.uniq_request = my_httptype + "-" + my_temp_method + "-" + request_url_host + "-" + url_path_string + "-" + self.req_param
            print(self.uniq_request)
            # 写入
            # add_segment
            self.mysqlutil.add_segment(self.encryutils.passwordenc(self.uniq_request, ""), self.uniq_request,
                                       my_temp_id, self.requestdict, self.responsedict)


# 监控返回包的等会再写
# self.check_result = self.json_sensitive(my_response_data, "uidstrfsdfsdfsdfsdfing")
# if self.check_result and len(self.check_result) > 0:
#     print(self.check_result)
#     self.result_data = ""
#     for key, value in self.check_result.items():
#         tempmsg = str(key) + "-" + value
#         if self.result_data == "":
#             self.result_data = self.result_data + tempmsg
#         else:
#             self.result_data = self.result_data + "|" + tempmsg
#     self.mysqlutil.write_vulnerability_to_db(requestdict, "check_sensitive_info", my_temp_id, my_time,
#                                              my_request_data, my_response_data, my_temp_method,
#                                              self.result_data)


# my_Segment_monitor = Segment_monitor()
# my_Segment_monitor.run({"username": "admin", "project": "天天基金20200918"})
