class dealrequest:
    def __init__(self):
        self.data = ""

    # request data return request_url_host request_url_path header_list contenttypestring
    def get_host_uri_header_type(self, my_request_data, my_temp_method):
        split_string = list(my_request_data.split("\r\n"))
        split_string.remove('')  # 删除所有的空元素

        header_list = split_string[1:]

        contenttypestring = ""  # 判断类型的contenttype
        hoststring = ""  # 判断类型的hoststring
        for hl in header_list:
            if "Content-Type:" in hl:
                contenttypestring = hl
            if "Host:" in hl:
                hoststring = hl

        header_list = "\n".join(header_list)

        request_url_host = str(hoststring).replace("Host: ", "")
        request_url_path = str(split_string[0]).replace(my_temp_method + " ", "").replace(" HTTP/1.1", "")
        return request_url_host, request_url_path, header_list, contenttypestring

    def get_cookie(self, cookie_data):
        cookie = {}
        try:
            beforecookiedict = {}
            aftercookiedict = {}
            counter = 0
            cookiedatalist = cookie_data.split(';')
            for line in cookiedatalist:

                if "=" in line[1:-1] and line[-1:] != "=":

                    beforecookiedict[counter] = line
                    if counter > 0:
                        key, value = beforecookiedict[counter - 1].split('=', 1)
                        cookie[key] = value
                        if counter == len(cookiedatalist) - 1:
                            # 最后一个正常的
                            key, value = beforecookiedict[counter].split('=', 1)
                            key = str(key).strip()
                            cookie[key] = value
                else:
                    if counter == 0:
                        beforecookiedict[counter] = line
                    else:
                        beforecookiedict[counter] = beforecookiedict[counter - 1] + ";" + line

                        if counter == len(cookiedatalist) - 1:
                            # 最后一个不正常的
                            key, value = beforecookiedict[counter].split('=', 1)
                            key = str(key).strip()
                            cookie[key] = value
                counter = counter + 1

        except Exception as e:
            cookie = {}
            print(e)
        return cookie

    # a=b&c=d  ->  {"a":"b","c":"d"}
    def url_data_to_dict(self, cookie_data):
        cookie = {}
        try:
            beforecookiedict = {}
            aftercookiedict = {}
            counter = 0
            if '&' not in cookie_data:
                cookiedatalist = [cookie_data]
            else:
                cookiedatalist = cookie_data.split('&')
            for line in cookiedatalist:
                templist = line.split("=")
                cookie[templist[0]] = templist[-1]

        except Exception as e:
            cookie = {}
            print(e)
        return cookie

    def get_headers(self, header_raw, my_temp_method):
        """
        通过原生请求头获取请求头字典
        :param header_raw: {str} 浏览器请求头
        :return: {dict} headers
        """

        origin_cookie = ""
        my_result_dict = {}
        request_post_data = ""
        if my_temp_method == "GET":

            for line in header_raw.split("\n"):
                # my_list = line.split(":")
                my_list = line.split(": ")
                if my_list[0] == 'Cookie':
                    origin_cookie = my_list[1]
                    continue
                if my_list[0] == "":
                    continue
                else:

                    my_result_dict[my_list[0]] = my_list[1]
            print(type(my_result_dict))
            print(my_result_dict)
            return request_post_data, origin_cookie, my_result_dict
        elif my_temp_method == "POST":

            for line in header_raw.split("\n"):
                # print(line)
                try:
                    if "{" in line.strip() and "}" in line.strip():
                        request_post_data = line
                        break  # 多行json数据暂未考虑
                    my_list = line.split(": ")
                    if my_list[0] == 'Cookie':
                        origin_cookie = my_list[1]
                        continue

                    if my_list[0] == "":
                        continue
                    else:

                        my_result_dict[my_list[0]] = my_list[1]
                except Exception as e:
                    print("切割失败")
                    print(e)
                    request_post_data = line

            return request_post_data, origin_cookie, my_result_dict
        else:
            return None, None, None

# mydealreq = dealrequest()
# result = mydealreq.url_data_to_dict("a=b&c=d&e=f")
# print(type(result))
