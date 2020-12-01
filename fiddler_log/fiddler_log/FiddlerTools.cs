using System.Data;
using System;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Fiddler;
using System.Windows.Forms;
using MySql.Data.MySqlClient;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

namespace fiddler_log
{
    public static class StreamExtension
    {
        
        // URL decode
        public static string DecodeUrlString(string url)
        {
            string newUrl;
            while ((newUrl = Uri.UnescapeDataString(url)) != url)
                url = newUrl;
            return newUrl;
        }

        // 判断是否json等格式
        public static string format_judge(string response_str)
        {
            string json_format = "Content-Type: application/json";
            if (response_str == "")
            {
                return "default string";
            }
            else
            {
                if (response_str.Contains(json_format))
                {
                    Global.response_format = "json";
                }
                string temp_result = "";
                temp_result = response_str.Replace("\"", " ");  // 临时替换，解决问题为主
                temp_result = temp_result.Replace("“", " ");  // 临时替换，解决问题为主  中文
                temp_result = temp_result.Replace("’", " ");  // 临时替换，解决问题为主  中文单引号
                temp_result = temp_result.Replace("<", " ");  // 临时替换，解决问题为主  英文尖括号
                temp_result = temp_result.Replace(">", " ");  // 临时替换，解决问题为主  英文尖括号
                temp_result = temp_result.Replace("-", " ");  // 临时替换，解决问题为主  -
                return temp_result.Replace("\'", " ");  // 临时替换，解决问题为主
            }
        }

        public static string gbk_utf_8(string str)
        {
            Encoding utf8;
            Encoding gb2312;
            utf8 = Encoding.GetEncoding("UTF-8");
            gb2312 = Encoding.GetEncoding("GB2312");
            if (str == "")
            {
                return "default string";
            }
            else
            {
                str = DecodeUrlString(str);
                byte[] gb = gb2312.GetBytes(str);
                gb = Encoding.Convert(gb2312, utf8, gb);
                return utf8.GetString(gb);
            }
        }

        public static string get_top_string(string str, int number)
        {
            int temp_number = UnicodeEncoding.Default.GetBytes(str).Length;
            if (temp_number < number)
            {
                return str;
            }
            else
            {
                return str.Substring(0, number);
            }

        }

    }

    public static class Global
    {
        public static bool isPhonenumber = false;  //判断是否是手机号
        public static bool isPhonenumberFlag = false;  //临时判断是否是手机号
        public static bool isCredit_id = false;  //判断是否是身份证
        public static bool isCredit_id_Flag = false;  //临时判断是否是身份证
        public static string databaseusername;
        public static string databasepassword;
        public static bool database_exception_flag; //判断数据异常 默认为空用来判断
        public static bool database_flag;
        public static string request_string;  // 请求数据
        public static string response_format;  // 请求格式
    }

    public class Mysql_utils
    {
        public MySqlConnection getmysqlcon()
        {
            string M_str_sqlcon = "Host=127.0.0.1;UserName=root;Password=t4o0$jor;Database=fiddler_log;Charset=utf8"; //根据自己的设置
            MySqlConnection myCon = new MySqlConnection(M_str_sqlcon);
            try
            {
                myCon.Open();
                //Console.WriteLine("已经建立连接");
                Global.database_exception_flag = false;
                return myCon;
            }
            catch (MySqlException ex)
            {
                //Console.WriteLine(ex.Message);
                //return "连接报错";
                MessageBox.Show("数据库账号密码不正确");
                Global.database_exception_flag = true;
                return myCon;
            }
            finally
            {
                myCon.Close();
            }
        }

    }

    public class FiddlerTools : IAutoTamper
    {
        UserInterface ui = null; //
        Mysql_utils mysql_util = new Mysql_utils();


        public static int GetRandomNumber(int min, int max)
        {
            int rtn = 0;

            Random r = new Random();
            byte[] buffer = Guid.NewGuid().ToByteArray();
            int iSeed = BitConverter.ToInt32(buffer, 0);
            r = new Random(iSeed);
            rtn = r.Next(min, max + 1);
            return rtn;
        }

        public FiddlerTools()
        {
            this.ui = new UserInterface();
        }
        public void AutoTamperRequestAfter(Session oSession)
        {
            //throw new NotImplementedException();
        }

        // 请求之前的
        public void AutoTamperRequestBefore(Session oSession)
        {
            
        }


        public static string MD5Hash(string input)
        {
            StringBuilder hash = new StringBuilder();
            MD5CryptoServiceProvider md5provider = new MD5CryptoServiceProvider();
            byte[] bytes = md5provider.ComputeHash(new UTF8Encoding().GetBytes(input));

            for (int i = 0; i < bytes.Length; i++)
            {
                hash.Append(bytes[i].ToString("x2"));
            }
            return hash.ToString();
        }

        //响应之后
        public void AutoTamperResponseAfter(Session oSession)
        {
            //请求响应数据写入
            if (UserInterface.bEnabled && Global.database_flag)
            //    if (UserInterface.bEnabled && Global.database_flag)
            {
                //get filetype and domain list
                var filetypeDomainList = new List<String>();
                var MethodList = new List<String>();
                foreach (KeyValuePair<string, string> kvp in UserInterface.configDataDictionary)
                {
                    if (kvp.Value == "filetype" || kvp.Value == "domain")
                    {
                        filetypeDomainList.Add(kvp.Key.ToString());
                    }

                    if (kvp.Value == "method")
                    {
                        MethodList.Add(kvp.Key.ToString());
                    }
                }



                string customers_tableName = "customers";
                string customers_exp_tableName = "customers_exp";


                int counter = 0;

                if (filetypeDomainList.Count > 0)
                {
                    foreach (string if_line in filetypeDomainList)
                    {
                        if (!oSession.uriContains(if_line))
                        {
                            counter++;
                        }
                    }
                }

                if (MethodList.Count > 0)
                {
                    foreach (string if_line_method in MethodList)
                    {
                        if (!oSession.HTTPMethodIs(if_line_method))
                        {
                            counter++;
                        }
                    }
                }

                if (counter == (filetypeDomainList.Count + MethodList.Count))
                {
                    string add_flag = "no exp";
                    // 越权排除列表打开
                    //b_Unauthorized_access_Enabled
                    if (UserInterface.b_Unauthorized_access_exp_Enabled)
                    {
                        add_flag = "exp";


                        string mId_exp = Guid.NewGuid().ToString("N");
                        string mTime_exp = oSession.Timers.ClientBeginRequest.ToString();
                        string temp_string2_exp = StreamExtension.gbk_utf_8(oSession.oRequest.headers + "\r\n" + oSession.GetRequestBodyAsString());
                        string mRequest_exp = StreamExtension.get_top_string(temp_string2_exp, 200000);
                        string temp_response_exp = StreamExtension.gbk_utf_8(oSession.GetResponseBodyAsString());
                        string mResponse_exp = StreamExtension.get_top_string(temp_response_exp, 200000);
                        string mProject_exp = UserInterface.projectnames;
                        string mUsername_exp = UserInterface.myusername;
                        
                        
                        string mhttptype_exp_string;
                        if (oSession.isHTTPS)
                        {
                            mhttptype_exp_string = "https";
                        }
                        else if (oSession.isFTP)
                        {
                            mhttptype_exp_string = "ftp";
                        }
                        else if (oSession.isTunnel)
                        {
                            mhttptype_exp_string = "tunnel";
                        }
                        else
                        {
                            mhttptype_exp_string = "http";
                        }
                        
                        string mTampMethod_exp;
                        if (oSession.RequestMethod == "POST")
                        {
                            mTampMethod_exp = "POST";
                        }
                        else if (oSession.RequestMethod == "GET")
                        {
                            mTampMethod_exp = "GET";
                        }
                        else if (oSession.RequestMethod == "OPTIONS")
                        {
                            mTampMethod_exp = "OPTIONS";
                        }
                        else if (oSession.RequestMethod == "HEAD")
                        {
                            mTampMethod_exp = "HEAD";
                        }
                        else if (oSession.RequestMethod == "PUT")
                        {
                            mTampMethod_exp = "PUT";
                        }
                        else
                        {
                            mTampMethod_exp = "DEFAULT";
                        }

                        Dictionary<string, string> exp_postData = new Dictionary<string, string>();
                        exp_postData.Add("token", UserInterface.mytoken);
                        exp_postData.Add("id", mId_exp);
                        exp_postData.Add("time", mTime_exp);
                        exp_postData.Add("request", mRequest_exp);
                        exp_postData.Add("response", mResponse_exp);
                        exp_postData.Add("method", mTampMethod_exp);
                        exp_postData.Add("httptype", mhttptype_exp_string);
                        exp_postData.Add("project", UserInterface.projectnames);
                        exp_postData.Add("username", UserInterface.myusername);
                        exp_postData.Add("add_flag", add_flag);
                        UserInterface.deal_post_data_urlformed("deal_post_data", exp_postData);
                    }

                    string mId = Guid.NewGuid().ToString("N");  
                    string mTime = oSession.Timers.ClientBeginRequest.ToString();

                    string temp_string2 = StreamExtension.gbk_utf_8(oSession.oRequest.headers + "\r\n" + oSession.GetRequestBodyAsString());
                    string mRequest = StreamExtension.get_top_string(temp_string2, 200000);

                    string temp_response_string2 = StreamExtension.gbk_utf_8(oSession.GetResponseBodyAsString());
                    string mResponse = StreamExtension.get_top_string(temp_response_string2, 200000);

                    string mhttptype_string;
                    if (oSession.isHTTPS)
                    {
                        mhttptype_string = "https";
                    }
                    else if (oSession.isFTP)
                    {
                        mhttptype_string = "ftp";
                    }
                    else if (oSession.isTunnel)
                    {
                        mhttptype_string = "tunnel";
                    }
                    else
                    {
                        mhttptype_string = "http";
                    }

                    string mTampMethod;
                    if (oSession.RequestMethod == "POST")
                    {
                        mTampMethod = "POST";
                    }
                    else if (oSession.RequestMethod == "GET")
                    {
                        mTampMethod = "GET";
                    }
                    else if (oSession.RequestMethod == "OPTIONS")
                    {
                        mTampMethod = "OPTIONS";
                    }
                    else if (oSession.RequestMethod == "HEAD")
                    {
                        mTampMethod = "HEAD";
                    }
                    else if (oSession.RequestMethod == "PUT")
                    {
                        mTampMethod = "PUT";
                    }
                    else
                    {
                        mTampMethod = "DEFAULT";
                    }


                    Dictionary<string, string> postData = new Dictionary<string, string>();
                    postData.Add("token", UserInterface.mytoken);
                    postData.Add("id", mId);
                    postData.Add("time", mTime);
                    postData.Add("request", mRequest);
                    postData.Add("response", mResponse);
                    postData.Add("method", mTampMethod);
                    postData.Add("httptype", mhttptype_string);
                    postData.Add("project", UserInterface.projectnames);
                    postData.Add("username", UserInterface.myusername);
                    postData.Add("add_flag", add_flag);
                    UserInterface.deal_post_data_urlformed("deal_post_data", postData);

                }
            }

            //漏洞数据写入
            string responseBodyEncode = oSession.GetResponseBodyEncoding().ToString();
            string responseString = oSession.GetResponseBodyAsString();

            // 判断手机号
            List<string> phonenumber_list = new List<string>();
            string responseString1 = responseString.Replace("<br>", " ");
            responseString = responseString1;

            string temp_response_string = StreamExtension.format_judge(responseString);   // 临时替换"为空格
            //MessageBox.Show(temp_response_string);
            string[] resultString_list = Regex.Split(temp_response_string, "\\s", RegexOptions.IgnoreCase);

            //手机号
            //bool isPhonenumberFlag  = false;
            Global.isPhonenumber = false;
            Global.isPhonenumberFlag = false;

            foreach (string i in resultString_list)
            {
                //bool temp_isPhonenumber;
                if (!(i.ToString() == ""))
                {
                    string yidong1 = @"^134[012345678]\d{7}$";
                    Regex yReg1 = new Regex(yidong1);
                    string yidong2 = @"^1[34578][0123456789]\d{8}$";
                    Regex yReg2 = new Regex(yidong2);
                    string xunihaoduan = @"^1[79]\d{9}$";
                    Regex xReg = new Regex(xunihaoduan);

                    string phone;
                    phone = i.ToString();
                    if (yReg1.IsMatch(phone) || xReg.IsMatch(phone) || yReg2.IsMatch(phone))
                    {
                        Global.isPhonenumber = true;
                        Global.isPhonenumberFlag = true;
                        phonenumber_list.Add(phone);
                    }
                    else
                    {
                        Global.isPhonenumber = false;
                    }
                }
            }

            // 判断身份证
            //MessageBox.Show("phonenumber_list" + phonenumber_list.Count);
            List<string> credit_id_list = new List<string>();
            Global.isCredit_id = false;
            Global.isCredit_id_Flag = false;
            bool isCreditID;


            foreach (string i in resultString_list)
            {
                //bool temp_isPhonenumber;
                if (!(i.ToString() == ""))
                {
                    //string shenfengzheng = @"^(\D).*[1-9]\d{5}(19|20)\d{2}[01]\d[0123]\d\d{3}[xX\d]$";
                    string shenfengzheng = @"^(\D).*[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx](\D).*|[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$";
                    Regex sReg = new Regex(shenfengzheng);

                    string id_string;
                    id_string = i.ToString();
                    if (sReg.IsMatch(id_string))
                    {
                        Global.isCredit_id = true;
                        Global.isCredit_id_Flag = true;                                
                        credit_id_list.Add(id_string);
                    }
                    else
                    {
                        Global.isCredit_id = false;
                        //Console.WriteLine("非正确的手机号");
                    }
                }
            }

            if (Global.isCredit_id_Flag)
            {
                Global.isCredit_id = true;
            }
            else
            {
                Global.isCredit_id = false;
            }


            if (Global.isPhonenumberFlag)
            {

                Global.isPhonenumber = true;

            }
            else
            {
                Global.isPhonenumber = false;
                //MessageBox.Show("not phone");
            }
            // 密码MD5
            bool isMD5;
            isMD5 = false;
            //var  passwordList = new List<string>();
            List<string> passwordList = new List<string>();
            List<string> md5List = new List<string>();
            passwordList.Add("admin");
            passwordList.Add("password");
            foreach (string md5hash in passwordList)
            {
                if (temp_response_string.Contains(MD5Hash(md5hash)))
                {
                    md5List.Add(md5hash);
                    isMD5 = true;
                }
            }


            if (isMD5 || Global.isPhonenumber || Global.isCredit_id)
            {
                //details string 
                string details;
                details = "";
                if (isMD5)
                {
                    details += "password MD5: " + String.Join(" ", md5List.ToArray());
                    //details += "\r\n" + "request:\r\n";
                }
                if (Global.isPhonenumber)
                {
                    details += "phonenumber: " + String.Join(" ", phonenumber_list.ToArray());
                    //details += "\r\n" + "request:\r\n";
                }
                if (Global.isCredit_id)
                {
                    details = "creditid_number: " + String.Join(" ", credit_id_list.ToArray());
                    //details += "\r\n" + "request:\r\n";
                }

                        
                string temp_request = StreamExtension.gbk_utf_8(oSession.oRequest.headers + "\r\n" + oSession.GetRequestBodyAsString());
                Global.request_string = temp_request;
                string temp_response = StreamExtension.gbk_utf_8(oSession.GetResponseBodyAsString());
                string uiresponse = StreamExtension.get_top_string(temp_response, 200000);

                // addreslt
                if (!(details == ""))
                {
                    this.ui.AddResult("\r\ndetails\r\n" + details + "\r\n" + "request:\r\n");
                    this.ui.AddResult(Global.request_string + "\r\n");
                    this.ui.AddResult("response : " + "\r\n " + uiresponse);                            
                }
            }
                

            
        }

        public void AutoTamperResponseBefore(Session oSession)
        {
            //throw new NotImplementedException();
            //oSession.GetRequestBodyAsString();
        }

        public void OnBeforeReturningError(Session oSession)
        {
            //throw new NotImplementedException();
        }

        public void OnBeforeUnload()
        {
            //throw new NotImplementedException();
        }

        public void OnLoad()
        {
            // here onload
            Global.database_flag = false; // 数据库准备好的标记
        }
    }
}