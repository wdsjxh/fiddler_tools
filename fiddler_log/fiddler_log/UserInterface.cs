using Fiddler;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using MySql.Data.MySqlClient;
using Microsoft.VisualBasic;
using System.Net;
using System.IO;
using Newtonsoft.Json;
using System.Data;

namespace fiddler_log


{
    public class Root
    {
        /// <summary>
        /// 
        /// </summary>
        public int code { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string data { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public string username { get; set; }
        /// <summary>
        /// 
        /// </summary>
        public List<string> project_names { get; set; }
        public Dictionary<string,string> result { get; set; }
    }



    class UserInterface : UserControl
    {
        Mysql_utils test_db_mysql_util = new Mysql_utils(); //MySQL数据库工具类 主要是用来测试数据库
        public static string myusername = "";
        public static string projectnames = "";
        public static string mytoken = "";
        public static string myurl = "";
        public static Dictionary<string, string> configDataDictionary = new Dictionary<string, string>();  // 过滤配置字典，验证token处获取

        private TabPage tabPage; //添加一个标签页 用来放置控件
        private CheckBox chkb_Enabled;  //用来启用或禁用插件
        private TextBox textBox_Result;  //用来保存最后的结果
        private Button btn_Clear;  //清空按钮
        private Button btn_TestDatabase;  //测试按钮
        private Label label1;  //用户名
        private Label label2;  //密码
        private TextBox username;
        private TextBox password;
        public static bool bEnabled;   //全局判断是否可用
        private Label label3;  //提示越权label
        private CheckBox chkb_Unauthorized_access;  //用来启用或禁用越权功能
        public static bool b_Unauthorized_access_Enabled;
        private Label label4;  //提示越权排除抓包
        private CheckBox chkb_Unauthorized_exp_access;  //用来确认越权排除抓包
        public static bool b_Unauthorized_access_exp_Enabled;
        private Label label5;  //显示登陆的用户名
        private ComboBox project_names; //项目名下拉框
        public delegate void Delegate_AddResult(string strUrl);//定义输出结果的委托
        public UserInterface()
        {
            bEnabled = false;
            b_Unauthorized_access_Enabled = false;
            this.InitializeUI();
            FiddlerApplication.UI.tabsViews.TabPages.Add(this.tabPage); //新建一个tabPage
        }

        public void InitializeUI() //初始化UI
        {
            this.tabPage = new TabPage("fiddler_tools");
            this.tabPage.ImageIndex = (int)Fiddler.SessionIcons.Timeline;
            this.tabPage.AutoScroll = true;

            this.chkb_Enabled = new CheckBox();
            this.chkb_Enabled.Top = 10;
            this.chkb_Enabled.Left = 20;
            this.chkb_Enabled.Text = "Enable";
            this.chkb_Enabled.Checked = false;  //初始化为不选中

            this.chkb_Unauthorized_access = new CheckBox();
            this.chkb_Unauthorized_access.Top = 40;
            this.chkb_Unauthorized_access.Left = 490;
            this.chkb_Unauthorized_access.Text = "Enable";
            this.chkb_Unauthorized_access.Checked = false;  //初始化为不选中

            this.chkb_Unauthorized_exp_access = new CheckBox();
            this.chkb_Unauthorized_exp_access.Top = 40;
            this.chkb_Unauthorized_exp_access.Left = 600;
            this.chkb_Unauthorized_exp_access.Text = "Enable";
            this.chkb_Unauthorized_exp_access.Checked = false;  //初始化为不选中

            //chkb_Unauthorized_exp_access

            this.btn_Clear = new Button();
            this.btn_Clear.Text = "Clear";
            this.btn_Clear.Left = 20;
            this.btn_Clear.Top = 40;
            this.btn_Clear.Enabled = false;

            //数据库相关
            this.label1 = new Label();
            this.label1.Text = "用户名";
            this.label1.Left = 150;
            this.label1.Top = 10;
            this.label1.Enabled = false;
            //this.label1.AutoSize = true;

            this.username = new TextBox();
            this.username.Text = "";
            this.username.Left = 250;
            this.username.Top = 10;
            this.username.Enabled = false;

            this.label2 = new Label();
            this.label2.Text = "密码";
            this.label2.Left = 150;
            this.label2.Top = 40;
            this.label2.Enabled = false;
            //this.label2.AutoSize = true;

            this.label3 = new Label();
            this.label3.Text = "是否启动越权";
            this.label3.Left = 490;
            this.label3.Top = 10;
            this.label3.Enabled = false;

            this.label4 = new Label();
            this.label4.Text = "越权排除列表";
            this.label4.Left = 600;
            this.label4.Top = 10;
            this.label4.Enabled = false;

            this.label5 = new Label();
            this.label5.Text = "未登录";
            this.label5.Left = 720;
            this.label5.Top = 10;
            this.label5.Enabled = false;

            this.project_names = new ComboBox();
            this.project_names.Left = 720;
            this.project_names.Top = 40;
            this.project_names.Enabled = false;

            this.password = new TextBox();
            this.password.Text = "";
            this.password.Left = 250;
            this.password.Top = 40;
            this.password.Enabled = false;

            this.btn_TestDatabase = new Button();
            this.btn_TestDatabase.Text = "连接数据库";
            this.btn_TestDatabase.Left = 400;
            this.btn_TestDatabase.Top = 10;
            this.btn_TestDatabase.Enabled = false;
            this.btn_TestDatabase.AutoSize = true;

            this.textBox_Result = new TextBox();
            this.textBox_Result.Top = 80;
            this.textBox_Result.Left = 20;
            this.textBox_Result.Width = 1000;
            this.textBox_Result.Height = 600;
            this.textBox_Result.ReadOnly = true;
            this.textBox_Result.Multiline = true;  //多行显示
            this.textBox_Result.ScrollBars = ScrollBars.Vertical;  //垂直滚动条

            this.tabPage.Controls.Add(this.chkb_Enabled);
            this.tabPage.Controls.Add(this.chkb_Unauthorized_access);
            this.tabPage.Controls.Add(this.chkb_Unauthorized_exp_access);
            this.tabPage.Controls.Add(this.btn_Clear);
            this.tabPage.Controls.Add(this.label1);
            this.tabPage.Controls.Add(this.label2);
            this.tabPage.Controls.Add(this.label3);
            this.tabPage.Controls.Add(this.label4);
            this.tabPage.Controls.Add(this.label5);
            this.tabPage.Controls.Add(this.project_names);
            this.tabPage.Controls.Add(this.username);
            this.tabPage.Controls.Add(this.password);
            this.tabPage.Controls.Add(this.btn_TestDatabase);
            this.tabPage.Controls.Add(this.textBox_Result);

            /*给chkb_Enabled添加CheckedChanged事件处理*/
            this.chkb_Enabled.CheckedChanged += new EventHandler(this.chkb_Enabled_CheckedChanged);
            this.chkb_Unauthorized_access.CheckedChanged += new EventHandler(this.chkb_Unauthorized_access_Enabled_CheckedChanged);
            this.chkb_Unauthorized_exp_access.CheckedChanged += new EventHandler(this.chkb_Unauthorized_access_exp_Enabled_CheckedChanged);
            this.btn_Clear.Click += new EventHandler(this.btn_Clear_Click);
            this.btn_TestDatabase.Click += new EventHandler(this.btn_TestDatabase_Click);
            this.project_names.SelectedIndexChanged += new EventHandler(this.ComboBox_project_names_CheckedChanged);
        }

        public void btn_TestDatabase_Click(object obj, EventArgs args)
        {
            MessageBox.Show("点击测试数据库");
            string mysql_username = username.Text;
            string mysql_password = password.Text;
            if (mysql_username == "")
            {
                MessageBox.Show("MySQL username can't be null");
            }
            else
            {
                MessageBox.Show("本地数据库功能已弃用");
                /*
                MySqlConnection test_db_mysqlcon = test_db_mysql_util.getmysqlcon_username_password(mysql_username, mysql_password);
                if (!Global.database_exception_flag)
                {
                    //保存用户名、密码
                    Global.databaseusername = mysql_username;
                    Global.databasepassword = mysql_password;
                    Global.database_flag = true;
                    test_db_mysqlcon.Open();
                    string sql_table_schema1 = @"
                    select * from information_schema.columns where table_schema = 'fiddler_log' and table_name = 'config';";
                    MySqlCommand cmd_schema1 = new MySqlCommand(sql_table_schema1, test_db_mysqlcon);
                    MySqlDataReader reader_schema1 = cmd_schema1.ExecuteReader();
                    if (reader_schema1.HasRows)
                    {
                        //String hasData = "yes";
                        //MessageBox.Show("fiddler log 中的config不为空");
                        reader_schema1.Close();
                    }
                    else
                    {
                        test_db_mysql_util.init_config_table("config");
                        reader_schema1.Close();
                    }
                    test_db_mysqlcon.Close();
                }
                */
            }

        }

        public void btn_Clear_Click(object obj, EventArgs args)
        {
            this.textBox_Result.Text = "";
        }

        /*
            *  url:POST请求地址
            *  postData:json格式的请求报文,例如：{"key1":"value1","key2":"value2"}
            */

        public static string PostUrl(string url, string postData)
        {
            string result = "";
            Stream stream = null;
            StreamReader reader = null;
            HttpWebResponse resp = null;
            HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);

            req.Method = "POST";
            req.Timeout = 1000 ;//设置请求超时时间，单位为毫秒
            req.ContentType = "application/json";

            if (!String.IsNullOrEmpty(postData))
            {
                using (var postStream = new StreamWriter(req.GetRequestStream()))
                {
                    postStream.Write(postData);
                }
                try {
                    resp = (HttpWebResponse)req.GetResponse();
                    if (resp != null) { 
                        stream = resp.GetResponseStream();
                        //获取响应内容
                        if (stream != null) { 
                            using (reader = new StreamReader(stream, Encoding.UTF8))
                            {
                                result = reader.ReadToEnd();
                            }
                        }
                    }
                    else
                    {
                        return result;
                    }

                }
                catch (NullReferenceException e)
                {
                    result = "";
                    return result;
                }
                catch (WebException e)
                {
                    using (WebResponse response = e.Response)
                    {
                        HttpWebResponse httpResponse = (HttpWebResponse)response;
                        MessageBox.Show(httpResponse.StatusCode.ToString());
                        result = "exception" + httpResponse.ToString();
                    }
                }
                finally
                {
                    // 释放资源
                    if (reader != null) reader.Close();
                    if (stream != null) stream.Close();
                    if (resp != null) resp.Close();
                }
            }
            return result;
        }

        // urlformed
        public static string PostUrl_urlformed(string url, Dictionary<string, string> postData)
        {
            string result = "";
            Stream stream = null;
            StreamReader reader = null;
            HttpWebResponse resp = null;
            HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);

            req.Method = "POST";
            req.Timeout = 1000;//设置请求超时时间，单位为毫秒
            req.ContentType = "application/x-www-form-urlencoded";

            StringBuilder builder = new StringBuilder();
            int i = 0;


            if (postData.Count >0 )
            {
                foreach (var item in postData)
                {
                    if (i > 0)
                        builder.Append("&");
                    builder.AppendFormat("{0}={1}", item.Key, item.Value);
                    i++;
                }

                using (var postStream = new StreamWriter(req.GetRequestStream()))
                {
                    postStream.Write(builder.ToString());
                }
                try
                {
                    resp = (HttpWebResponse)req.GetResponse();
                    if (resp != null)
                    {
                        stream = resp.GetResponseStream();
                        //获取响应内容
                        if (stream != null)
                        {
                            using (reader = new StreamReader(stream, Encoding.UTF8))
                            {
                                result = reader.ReadToEnd();
                            }
                        }
                    }
                    else
                    {
                        return result;
                    }

                }
                catch (NullReferenceException e)
                {
                    result = "";
                    return result;
                }
                catch (WebException e)
                {
                    using (WebResponse response = e.Response)
                    {
                        HttpWebResponse httpResponse = (HttpWebResponse)response;
                        MessageBox.Show(httpResponse.StatusCode.ToString());
                        result = "exception" + httpResponse.ToString();
                    }
                }
                finally
                {
                    // 释放资源
                    if (reader != null) reader.Close();
                    if (stream != null) stream.Close();
                    if (resp != null) resp.Close();
                }
            }
            return result;
        }

        //请求数据发送 deal_post_data
        public static void deal_post_data(string url, string data_string)
        {
            string get_config_result = "default";
            try { 
                get_config_result = PostUrl(myurl.Replace("deal_capture_token", url), data_string);
                /*
                Root rt_deal_post_data = JsonConvert.DeserializeObject<Root>(get_config_result);
                if (rt_deal_post_data.code == 20000 && rt_deal_post_data.data == "success")
                {
                    MessageBox.Show(rt_deal_post_data.ToString());
                }
                else
                {
                    MessageBox.Show("返回请求数据发送字典为空");
                }
                */
            }
            catch (NullReferenceException e)
            {
                //MessageBox.Show("空引用异常" + e);  //不处理
            }
        }

        //请求数据发送 deal_post_data_urlformed  www-urlformed
        public static void deal_post_data_urlformed(string url, Dictionary<string, string> data_string)
        {
            string get_config_result = "default";
            try
            {
                get_config_result = PostUrl_urlformed(myurl.Replace("deal_capture_token", url), data_string);

                /*
                Root rt_deal_post_data = JsonConvert.DeserializeObject<Root>(get_config_result);
                if (rt_deal_post_data.code == 20000 && rt_deal_post_data.data == "success")
                {
                    MessageBox.Show(rt_deal_post_data.ToString());
                }
                else
                {
                    MessageBox.Show("返回请求数据发送字典为空");
                }
                */
            }
            catch (NullReferenceException e)
            {
                //MessageBox.Show("空引用异常" + e);  //不处理
            }
        }


        //处理获取配置文件 get_config
        public static Dictionary<string, string> get_config(string url, string data_string)
        {
            Dictionary<string, string> selectDataDictionary = new Dictionary<string, string>();
            string get_config_result = "default";
            get_config_result = PostUrl(myurl.Replace("deal_capture_token", url), data_string);
            Root rt_get_config = JsonConvert.DeserializeObject<Root>(get_config_result);
            if (rt_get_config.code == 20000 && rt_get_config.data == "success")
            {
                MessageBox.Show(rt_get_config.ToString());
                selectDataDictionary = rt_get_config.result;
            }
            else
            {
                MessageBox.Show("返回config字典为空");
                selectDataDictionary = null;
            }
            return selectDataDictionary;
        }
    

        public void chkb_Enabled_CheckedChanged(object obj, EventArgs args)
        {
            if (this.chkb_Enabled.Checked) {
                string str = Interaction.InputBox("直接从网页端复制", "填写抓包token", "", -1, -1);
                if (!String.IsNullOrEmpty(str))
                {
                    //MessageBox.Show(str);
                    //MessageBox.Show("即将请求api");
                    string[] after = str.Split(new char[] { '|' });
                    
                    if (after.Length < 2)
                    {
                        MessageBox.Show("token格式不正确");
                        bEnabled = false;
                    }
                    else { 
                        myurl = after[0];
                        mytoken = after[1];
                        string jsonText = "{\"token\":\"" + mytoken + "\"}";

                        try
                        {
                            string response_result = PostUrl(myurl, jsonText);
                            //校验用户是否正常
                            Root rt = JsonConvert.DeserializeObject<Root>(response_result);

                            if (!String.IsNullOrEmpty(rt.username))
                            {
                                this.label5.Text = "您好：" + rt.username;
                                myusername = rt.username;
                                Global.database_flag = true;  // 原来的数据库标识
                                foreach (string project in rt.project_names)
                                {
                                    this.project_names.Items.Add(project);
                                }
                                foreach (KeyValuePair<string, string> kvp in rt.result)
                                {
                                    configDataDictionary.Add(kvp.Key, kvp.Value);
                                }
                            }
                            else
                            {
                                MessageBox.Show("用户校验不成功");
                                bEnabled = false;
                            }
                        }
                        catch (NullReferenceException e)
                        {
                            MessageBox.Show("验证token 空引用异常" + e);
                        }
                    }
                }
                else
                {
                    MessageBox.Show("抓包token为空");
                }
            }
            else
            {
                this.label5.Text = "未登录";
                this.project_names.Items.Clear();
            }
            this.SuspendLayout();
            bEnabled = this.chkb_Enabled.Checked;
            this.btn_Clear.Enabled = bEnabled;
            this.label1.Enabled = bEnabled;
            this.label2.Enabled = bEnabled;
            this.label3.Enabled = bEnabled;
            this.label4.Enabled = bEnabled;
            this.label5.Enabled = bEnabled;
            this.project_names.Enabled = bEnabled;
            this.username.Enabled = bEnabled;
            this.password.Enabled = bEnabled;
            this.btn_TestDatabase.Enabled = bEnabled;
            this.chkb_Unauthorized_access.Enabled = bEnabled;
            this.chkb_Unauthorized_exp_access.Enabled = bEnabled;
            this.ResumeLayout();
        }
        // 下拉框选择改变
        public void ComboBox_project_names_CheckedChanged(object obj, EventArgs args)
        {
            //MessageBox.Show(project_names.SelectedItem.ToString());
            projectnames = project_names.SelectedItem.ToString();
        }

        public void chkb_Unauthorized_access_Enabled_CheckedChanged(object obj, EventArgs args)
        {
            b_Unauthorized_access_Enabled = this.chkb_Unauthorized_access.Checked;
        }

        public void chkb_Unauthorized_access_exp_Enabled_CheckedChanged(object obj, EventArgs args)
        {
            b_Unauthorized_access_exp_Enabled = this.chkb_Unauthorized_exp_access.Checked;
        }

        public void AddResult(string strUrl)
        {
            if (!this.textBox_Result.InvokeRequired)
                this.textBox_Result.AppendText(strUrl + "\r\n");
            else
            {
                Delegate_AddResult delegate_addresult = new Delegate_AddResult(this.AddResult);
                this.textBox_Result.Invoke(delegate_addresult, strUrl);
            }
        }

    }
}
