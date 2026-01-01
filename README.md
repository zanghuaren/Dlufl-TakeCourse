## 更新日志
- 2026年1月1日：代码已重构，支持自动登录，根据课程名称自动匹配课程而不再是需要手动输入课程ID。
- 2025年7月9日：教务系统升级，部分接口变动，抢课脚本已不再可用。
- 2025年1月6日：初版代码完成。

 ## 介绍
 写这个脚本的初衷是高考完暑假时在Github搜索大外的抢课脚本没有搜到，而其他很多学校都有，光复大外计算机水平，义不容辞。

 ## 使用

 ### 前置准备
 安装[node.js](https://nodejs.org/en/download),用于登录的js加密。   
 
 pip安装引入的库：   
 
`
 pip install tabulate requests PyExecJS beautifulsoup4
`
### 脚本配置
打开main.py,在前几行填写你的账号密码级想选的选修课和体育课。  

```
USERNAME = "请填写你的账号"
PASSWORD = "请填写你的密码"
xx_except_pool = ["选修课程名称1", "选修课程名称2", "选修课程名称3"]
ty_except_pool = {"体育课名称1": "老师名称1"}
```
体育课填写示例：   
```
ty_except_pool = {"羽毛球": "桃田贤斗"}
```
在选课开始前可以访问教务系统的[学期理论课表](http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xskb/xskb_list.do)及[执行计划查询](http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/pyfa/pyfa_query)来确定自己要选的选修和体育课。

### 使用
运行main.py

## 其它说明
公共必修（大一有，如生命安全、健康教育等）和公共选修（网课及线下课，大学至少选一门线下课）基本没有竞争，什么时候都能选，因此脚本中没有选。如有需要请自行手动选择。



