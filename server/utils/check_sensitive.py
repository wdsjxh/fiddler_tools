import re

passwordmd5 = [
    "21232f297a57a5a743894a0e4a801fc3", "e10adc3949ba59abbe56e057f20f883e", "b0c611aa3ddbdd92335e5c3d7c4cf8e4",
    "a8abeb68d2492961e2cb2e580268057f", "8762eb814817cc8dcbb3fb5c5fcd52e0", "7fef6171469e80d32c0559f88b377245",
    "af1703dbc1c2fdc71cb1f623a577e82a", "c1cfdbe82f98c390ff00256027540049", "546dd0e1a6f69231d7ab0af11a679397",
    "ee808bee7c7800120a9323e535725d5b", "047014efbe9853eba6576f768a4e72b2", "012e090184b5b07608c6bfdd0ae598d9"
]


def check_bank_card(value):
    total = 0
    card_num_length = len(value)
    for item in range(1, card_num_length + 1):
        t = int(value[card_num_length - item])
        if item % 2 == 0:
            t *= 2
            total += t if t < 10 else t % 10 + t // 10
        else:
            total += t
    if total % 10 == 0:
        return True
    else:
        return False


def check_ID(value):
    if len(value) == 18:
        id_sum = 0
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        for i in range(17):
            id_sum = id_sum + int(value[i]) * weights[i]
            check_dict = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
        if check_dict[id_sum % 11] == value[-1]:
            return True


# 参数一般是json返回包值里面判断,相对fiddler插件那里判断不太相同
def re_bank_card(responsestring):
    result19 = re.findall(r'\d{19}', responsestring)
    if len(result19) > 0:
        return check_bank_card("".join(result19))
    else:
        result16 = re.findall(r'\d{16}', responsestring)
        if len(result16) > 0:
            return check_bank_card("".join(result16))
    return False


def re_check_id(responsestring):
    resultid = re.findall(r'^\d{17}[\d|X]$', responsestring, re.I)
    if len(resultid) > 0:
        return check_ID("".join(resultid))
    return False


def re_check_mobile(responsestring):
    result_mobile = re.findall(r'^1[3|4|5|7|8][0-9]{9}$', responsestring)
    if len(result_mobile) > 0:
        return True
    else:
        return False


# 敏感信息password md5
def check_passwordmd5(data):
    # password
    print("md5")
    for line in passwordmd5:
        if line == data:
            return True
    return False


# return dict
def run(data):
    print(data)
    print(type(data))
    data = str(data)
    result = ""
    if re_check_mobile(data):
        result = "手机号"
    elif re_bank_card(data):
        result = "银行卡"
    elif re_check_id(data):
        result = "身份证"
    elif check_passwordmd5(data):
        result = "敏感密码MD5"
    return result
