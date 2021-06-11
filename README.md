# 被动扫描系统使用说明 


## 项目说明

​		被动扫描系统项目,主要功能为通过fiddler插件保存数据包并入库，用户使用web管理界面自定义规则扫描漏洞，漏洞结果扫猫过程中实时展示，目前主要是检测越权和敏感信息检测等模块。

## 技术架构

* Fiddler插件：C#开发   VS2015编译  对应项目fiddler_log目录

* 网站前端：Nodejs Vue 2.9 vue-admin-template前端框架   对应项目client

* 后端：Flask网站接口，Python完成漏洞检测。  对应项目目录server

* release：  编译好的文件

* 数据库: MySQL5.6

![structure](./img/pic.png)

首页

![Dashboard](./img/Snipaste_2020-11-30_16-15-29.png)

## Change:

2021.6.11——添加docker部署

## Docker安装（推荐）以Kali2021.1版本部署为例

1. 宿主机MySQL配置，目前使用的宿主机MySQL保存数据

   1. 新建数据库fiddler_log

      ```mysql
      CREATE fiddler_log IF NOT EXISTS
      ```

   2. 导入SQL文件，生成表结构

      导入项目根目录下fiddler_log_structure.sql文件

      ```Mysql
      source ./fiddler_log_structure.sql
      ```

   3. 配置docker访问宿主机MySQL权限

      1. iptables开启允许docker访问宿主机MySQL端口

         172.17.0.2是docker容器默认IP，请根据实际情况修改

         ```bash
         sudo iptables -I INPUT -s 172.17.0.2 -p tcp --dport 3306 -j ACCEPT
         ```

      2. 设置MySQL监听非本机

         修改MySQL配置文件，Kali是在50-server.cnf文件

         ```bash
         cd /etc/mysql/mariadb.conf.d
         ```

         ```bash
         sudo vim 50-server.cnf
         ```

         找到bind-address 127.0.0.1那行，最前面添加#注释

         重启MySQL服务

         ```bash
         sudo systemctl restart  mysql.service
         ```

      3. 授予docker对Mysql数据库操作权限

         ```bash
         sudo mysql -uroot -p
         ```

         进入MySQL后，授权对应docker容器IP（172.17.0.2）访问fiddler_log数据库权限

         ```mysql
         GRANT ALL PRIVILEGES ON fiddler_log.* TO 'root'@'172.17.0.2' IDENTIFIED BY 'PASSWORD' WITH GRANT OPTION; 
         ```

         刷新权限

         ```mysql
         flush privileges;
         ```

         重启MySQL服务

         ```bash
         sudo systemctl restart  mysql.service
         ```

2. 拉取Docker镜像

   ```bash
   sudo docker push kalagin/fiddler_tools:v1.0
   ```

3. 启动容器并修改后端接口

   ```bash
   sudo docker run -ti -p 80:80 -e MYSQL_URI=mysql://root:PASSWORD@192.168.32.132:3306/fiddler_log -d kalagin/fiddler_tools:v1.0
   ```

   其中PASSWORD对应数据库密码，IP对应宿主机IP

   查看容器CONTAINER ID

   ```bash
   sudo docker ps -a
   ```

   进入容器

   ```bash
   sudo docker exec -it CONTAINER_ID bash
   ```

   ```bash
   cd /fiddler_tools/client/dist/
   ```

   config.js是配置后端接口文件

   修改app_api_url为自己ip地址，VPS的话是外网IP，注意后面带一个/api

4. 重启容器

   ```bash
   sudo docker restart CONTAINER_ID
   ```

   访问 http://192.168.32.132 即可，VPS直接对应外网IP

## 源码安装

插件编译
1. 可参考fiddler插件开发环境，添加fiddler.exe到项目中。
2. 添加Newtonsoft.Json.dll到项目引用
3. 项目编译，release提供了编译好的插件fiddler_log.dll和Newtonsoft.Json.dll

后端安装
1. `python3 -m pip install -r requirements.txt`
2. 新建数据库fiddler_log(utf8编码)，导入数据库文件fiddler_log_structure.sql
3. config/dbconfig.py中的mysqlhost数据库配置，数据库名**fiddler_log**
   **my_api**填写域名或ip
4. flask_main.py 本地开发环境，flask_main_online.py 线上环境
5. 运行`python3 flask_main.py` 本地  运行`python3 flask_main_online.py` 线上环境
6. 再运行监听扫描状态文件scan_main.py `python3 scan_main.py`

开发数据库使用的MySQL5.6，导入数据库过程中可能会出现specified key too long 709 byte，自行修改数据库配置
线上部署推荐使用Flask+Nginx+Gunicorn+HTTPS，详细部署请参考其他教程

前端打包
 1. 安装依赖

    ```bash
     npm install
    ```

2. 修改接口地址  
    修改public/config.js中app_api_url为自己IP地址，注意带/api

3. 开发环境 `npm run dev`  上线打包 `npm run build:prod`

4. 打包好的dist文件夹放在后端根目录下,与flask文件中 static_folder="./dist/static",template_folder="./dist")对应

## 使用步骤

1. 注册web后台账号，目前没有做限制

![Snipaste_2020-11-05_16-39-22](./img/Snipaste_2020-11-05_16-39-22.png)

2. 新建项目

   项目名称作为标识用，默认会生成一个default项目。

3. 下载安装fiddler被动扫描插件

   - 安装好fiddler软件。

   - 复制fiddler插件( fiddler_log.dll )到C:\Users\用户名\Documents\Fiddler2\Scripts目录下，该目录初次打开fiddler软件会自动生成。

     手动编译或者直接使用release/fiddler_log.dll

   - 复制插件所需要的json库（ Newtonsoft.Json.dll ）到fiddler安装目录下的Scripts目录下

     使用release/Newtonsoft.Json.dll

4. 复制web上的抓包token

   ![](./img/Snipaste_2020-11-05_17-22-40.png)

5. fiddler被动扫描插件处启动并选择项目

   - fiddler标签栏找到“fiddler_tools”插件

   ![](./img/Snipaste_2020-11-05_17-26-54.png)

   - 复制从网页端复制的token

    ![](./img/Snipaste_2020-11-05_17-24-56.png)

   - 选择项目

     选择创建过的项目

​			







​	

6. 配置好fiddler代理端口开始抓包，抓包结束

7. 配置具体扫描规则

   在网页端扫描规则配置处可新建、编辑具体规则，下面说明用的“默认规则”

   - 配置名称，必填且不可修改，用作配置标识
   - 越权检测主要分为替换cookie和替换uid两种类型，替换cookie主要是扫描不需要cookie就能成功越权和只是修改cookie就能越权的情况，替换uid是扫描修改数据中指定参数值便能越权情况，可以是天天基金uid、通行证passportid等。
   - 替换cookie：填写替换当前的cookie
   - 原始uid：待检测的字段值
   - 启动敏感信息：检测手机号、身份证、银行卡
   - 启动监控：检测返回包中包含的uid、phone等字段，后续可配置

   ![](./img/Snipaste_2020-11-05_17-49-13.png)

8. 开启扫描

   Dashboard/项目配置/扫描任务启动配置，选择配置之后启动

<font color=red>备注：用户名、密码处已废弃，选择"越权排除列表"表示当前抓取公共页面或者访客用户登录，为了降低访问到新闻页、公开数据页导致的越权检测误报。</font>

本项目仅供技术交流，请勿用于商业及非法用途，如产生法律纠纷与本人无关
