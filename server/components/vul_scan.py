from multiprocessing import Pool
from multiprocessing import cpu_count
import json
import copy

from data.myData import myData
from components.judge_out_of_access import Judge_out_of_access
from components.payloadlist_xss import Payloadlist_xss
from components.check_sensitive_info import Check_sensitive_info
from components.segment import Segment
from components.monitor import Monitor
from utils.mysqlutils import mysqlutil


class Vul_scan(object):

    def __init__(self):
        # 初始化扫描功能
        # app  启动写在构造函数中
        self.judge_out_of_access = Judge_out_of_access()
        self.payloadlist_xss = Payloadlist_xss()
        self.check_sensitive_info = Check_sensitive_info()
        self.segment = Segment()
        self.monitor = Monitor()
        self.mysqlutil = mysqlutil()
        self.global_data = myData()
        self.proxyList = "test"
        self.requestdict = {}
        self.finishdict = {}
        self.origin_requestdict = {}  # 原始字典，包含id

    def run_judge_out_of_access(self, requestdict):
        self.judge_out_of_access.run(requestdict)

    def run_payloadlist_xss(self, requestdict):
        self.payloadlist_xss.run(requestdict)

    def run_check_sensitive_info(self, requestdict):
        self.check_sensitive_info.run(requestdict)

    def run_segment(self, requestdict):
        self.segment.run(requestdict)

    def run_monitor(self, requestdict):
        self.monitor.run(requestdict)

    def work(self, requestdict):
        pool = Pool(processes=cpu_count() + 1)
        print("读取配置")  # requestdict中有id
        func = []

        out_of_access_dict = {}
        myresultlist = self.mysqlutil.get_config_from_projectid(requestdict)
        for line in myresultlist:
            temp_func = 'self.' + line["scan_type_run_name"]
            if temp_func not in func:
                func.append(eval(temp_func))
                if line["scan_type_name"] == "Judge_out_of_access":
                    out_of_access_dict = json.loads(line["content"])

        self.global_data.set_cookie_first(out_of_access_dict["token"])
        self.global_data.set_origin_userid(out_of_access_dict["越权uid配置"]["origin_userid"])
        self.global_data.set_userid_first(out_of_access_dict["越权uid配置"]["userid_first"])
        self.global_data.set_userid_second(out_of_access_dict["越权uid配置"]["userid_second"])
        # print("测试写入全局配置")
        # print(self.global_data.get_userid_first())
        # todo 初始化 全局变量
        self.requestdict = requestdict
        self.origin_requestdict = copy.deepcopy(self.requestdict)
        remove = requestdict.pop("id", "404")
        for fun in func:
            pool.apply_async(fun, args=(self.requestdict,))

        pool.close()
        pool.join()

        self.finishdict["id"] = remove
        self.finishdict["status"] = "stop"
        self.mysqlutil.set_project_status(self.finishdict)
