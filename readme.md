根目录非本地测试必要文件说明：

django.wsgi是apache部署的必要文件，其中的sys.path.append(r'C:')是在windows上部署时添加的工程所在目录。

httpd.conf是apache的配置文件备份

iamnotdbfile是数据库文件

如果网站有异常会将异常记录到log.txt

openshiftlibs.py、renamesettings.sh 和settings_local.py是部署到openshift需要上需要用到的文件

---------------------------------------

极客和校赛的切换：

第二个PLATFORM_HOST请修改为对应的比赛网址
PLATFORM_MODE修改为对应的比赛名称：信息安全大赛 或者 极客大挑战

geekchallenge目录下的templates目录下修改home.html和base.html对应的网页标题和内容。

---------------------------------------

后台地址：http://hostname/admin
在geek目录下的urls.py中可以修改

---------------------------------------

数据库同步命令：python manage.py syncdb
数据文件不存在时会重新生产数据库和设置后台管理员帐号和密码

---------------------------------------

settings中有私人邮箱帐号和密码，请使用平台的同学不要随意修改。

---------------------------------------

论坛里面可以回帖使用微博的@功能哟。后台有方便打印的自定义的统计信息表格
