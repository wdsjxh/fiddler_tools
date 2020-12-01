# coding:utf8
from components.vul_scan import Vul_scan
import time
from utils.mysqlutils import mysqlutil

if __name__ == '__main__':
    flag = False
    vul_scan = Vul_scan()
    mysqlutil = mysqlutil()  # 每次实例化一个对象，防止类成员变量重复

    while 1:
        print("开始循环监听扫描")
        # 监听事件，或者读数据库字段
        # 标记启动那里需要的是写入数据库值
        # 循环读取扫描状态表
        resultlist = mysqlutil.get_project_status("scanning")
        if len(resultlist) == 0 or resultlist is None:
            flag = False
        else:
            flag = True
        if flag:
            print("开始执行")
            for resultline in resultlist:
                # 扫描需要id  用户名 项目名参数 OK  顺序
                print("vul_scan")
                vul_scan.work(resultline)
        resultlist.clear()
        time.sleep(3)
