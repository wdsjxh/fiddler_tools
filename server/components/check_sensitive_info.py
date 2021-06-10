import time
import sys
sys.path.append("../")
from utils.mysqlutils import mysqlutil
from utils.deal_dict_class import returnreplacejson_payload
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("fiddler_tools.log", encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Check_sensitive_info:
    def __init__(self):
        self.requestdict = {}
        self.mysqlutil = mysqlutil()
        self.check_result = {}
        self.result_data = ""

    # 调用替换json字典
    # json返回包替换时间戳 返回字典
    def json_sensitive(self, jsonstring, uidstring):
        result_dict = {}
        if not jsonstring:
            return None
        try:
            dict_json = json.loads(jsonstring)
        except Exception as e:
            print(e)
            return {}

        tempresult = returnreplacejson_payload(
            dict_json, "check_sensitive_info",
            uidstring)[0]
        if tempresult:
            result_dict = tempresult
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

            self.check_result = self.json_sensitive(my_response_data, "uidstrfsdfsdfsdfsdfing")
            if self.check_result and len(self.check_result) > 0:
                print(self.check_result)
                self.result_data = ""
                for key, value in self.check_result.items():
                    tempmsg = str(key) + "-" + value
                    if self.result_data == "":
                        self.result_data = self.result_data + tempmsg
                    else:
                        self.result_data = self.result_data + "|" + tempmsg
                    # 返回包  json
                # logger.warning(self.result_data)
                self.mysqlutil.write_vulnerability_to_db(requestdict, "漏洞", "信息泄露", "check_sensitive_info", my_temp_id,
                                                         my_time,
                                                         my_request_data, my_response_data, my_temp_method,
                                                         self.result_data)

# my_Check_sensitive_info = Check_sensitive_info()
# my_Check_sensitive_info.run({"username": "admin", "project": "checkid"})
