# coding:utf-8
import time
import datetime

# timeStamp = 1551077515
# timeArray = time.localtime(timeStamp)
# formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
# print (formatTime)
# 返回包排除掉的字符串
expstringlist = ["--"]


def datetime_compare(oritime, starttime, stoptime):
    d_ori = datetime.datetime.strptime(oritime, '%Y/%m/%d %H:%M:%S')
    d_start = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
    d_stop = datetime.datetime.strptime(stoptime, '%Y-%m-%d %H:%M:%S')
    if d_ori > d_start and d_ori < d_stop:
        return True
    else:
        return False


# 生成年月字典数据
def make_year_month_dict(result_dict):
    result_list = []
    today = datetime.date.today()
    formatted_today = today.strftime('%Y')
    for i in range(1, 13):
        tempmonth = formatted_today + (str(i).zfill(2))
        if tempmonth in result_dict.keys():
            result_list.append(int(result_dict[tempmonth]))
        else:
            result_list.append(0)

    return result_list

# 原始 时间加8小时变成/
def datetime_add8(oritime):
    dt = datetime.datetime.strptime(oritime, '%Y-%m-%dT%H:%M:%S.000Z')
    # print(type(dt))
    # print(dt)
    eta = (dt + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    # print(eta)
    return eta
    # print(type(eta))
    # print(str(dt).replace("-", "/"))


def timestamptodate(string):
    # 今天日期
    today = datetime.date.today()

    # 昨天时间
    lastweekday = today - datetime.timedelta(days=7)
    # print(yesterday)
    # 昨天开始时间戳
    lastweekday_start_time = int(time.mktime(time.strptime(str(lastweekday), '%Y-%m-%d')))
    # print(lastweekday_start_time)
    # print(int(time.time()))
    try:
        timeArray = time.localtime(string)
        # print(timeArray)
        formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # print(formatTime)
        # print(type(formatTime))
        #
        # print("string")
        # print(string)
        # 过去一周之内的时间戳
        if int(string) <= int(time.time()) and int(string) >= lastweekday_start_time:
            return True
        else:
            print("非一周内时间")
            return False
    except:
        print("非时间戳")
        return False


# 判断10or13位纯数字，是否一周内时间戳
def istimestamp(string):
    string = str(string).strip()
    if str(string).isdigit():
        if len(str(string)) == 13:
            string = int(float(int(string) / 1000))
            print(string)
            if timestamptodate(int(string)):
                return True
            else:
                return False
        elif len(str(string)) == 10:
            if timestamptodate(int(string)):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


# 判断是否任意时间字符串
def isdatetimestring(datetimestring):
    datetimestring = str(datetimestring).strip()
    try:
        if ":" in datetimestring:
            if " " in datetimestring:
                time.strptime(datetimestring, "%Y-%m-%d %H:%M:%S")
            elif "T" in datetimestring:
                time.strptime(datetimestring, "%Y-%m-%dT%H:%M:%S")
        else:
            time.strptime(datetimestring, "%Y-%m-%d")
        return True
    except:
        return False


# 判断排除的字符串
def isexpstring(datetimestring):
    for expline in expstringlist:
        if expline == datetimestring:
            return True
    return False


# if istimestamp(1595905004):
#     print("is")
# else:
#     print("not")
# if isdatetimestring("2020-08-04 08:08:03"):
#     print("is datetime")
# else:
#     print("no datetime")

# print(int(time.time()))
# 1595901860403
# print(datetime_compare("2020/08/21 10:26:50", "2020-09-08 10:26:50","2020-09-08 10:26:50"))
# print(make_year_month_dict({}))
