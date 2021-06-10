import time
import sys
sys.path.append("../")
from utils.mysqlutils import mysqlutil
from utils.deal_dict_class import return_json_look_up
from utils.dealrequest import dealrequest
import json
import logging
from utils.encryutils import encryutils
from config.config import MONITOR_LIST

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("fiddler_tools.log", encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Monitor:
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
        self.write_flag = False

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

    def run(self, requestdict):
        my_request_list = self.mysqlutil.get_most_customers(requestdict)
        for line in my_request_list:

            my_temp_method = line["method"]
            my_request_data = line["request"]
            my_response_data = line["response"]
            my_temp_id = line["id"]
            my_time = line["time"]
            my_httptype = line["httptype"]

            self.responsedict = self.json_segment_monitor(my_response_data, "fsaadfsf435456")

            self.result_data = "监控信息-"
            for monitor_line in MONITOR_LIST:
                if monitor_line in str(self.responsedict.keys()):
                    print(str(self.responsedict.keys()))
                    self.result_data = self.result_data + "-" + monitor_line
                    self.write_flag = True
            if self.write_flag:
                self.mysqlutil.write_vulnerability_to_db(requestdict, "监控", "监控", "monitor", my_temp_id, my_time,
                                                         my_request_data, my_response_data, my_temp_method,
                                                         self.result_data)
                self.write_flag = False
                self.result_data = ""

# my_monitor = Monitor()
# my_monitor.run({"username": "admin", "project": "天天基金20200918"})
