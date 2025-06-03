1、安装依赖：
pip install flask requests beautifulsoup4

2、修改端口，代码默认是5013

3、启动：python app.py

4、访问：

今日要闻: http://127.0.0.1:{port}/api/peoples_daily_news

指定日期 (例如2023-10-01): http://127.0.0.1:{port}/api/peoples_daily_news?date=2023-10-01


5、返回结果示例：
```json
{
  "data": [
    {
      "date": "2025年06月03日13:49",
      "link": "http://finance.people.com.cn/n1/2025/0603/c1004-40492429.html",
      "title": "头条新闻：山村之变 老乡消费挺“潮”"
    },
    {
      "date": "2025年06月03日11:25",
      "link": "http://opinion.people.com.cn/n1/2025/0603/c1003-40492458.html",
      "title": "头条新闻：加快形成与新质生产力相适应的新型生产关系"
    },
    {
      "date": "2025年06月03日09:55",
      "link": "http://finance.people.com.cn/n1/2025/0603/c1004-40492425.html",
      "title": "头条新闻：振兴三题"
    },
    {
      "date": "2025年06月03日05:42",
      "link": "http://finance.people.com.cn/n1/2025/0603/c1004-40492423.html",
      "title": "头条新闻：广西持续扩大高水平对外开放"
    },
    {
      "date": "2025年06月03日10:10",
      "link": "http://society.people.com.cn/n1/2025/0603/c1008-40492969.html",
      "title": "最高法发布生态环境保护专题指导性案例"
    },
    {
      "date": "2025年06月03日11:20",
      "link": "http://society.people.com.cn/n1/2025/0603/c1008-40493037.html",
      "title": "端午节假期590.7万人次出入境"
    },
    {
      "date": "2025年06月03日05:58",
      "link": "http://finance.people.com.cn/n1/2025/0603/c1004-40492430.html",
      "title": "前4月我国交通投资高位运行 水路投资同比增长10.4%"
    },
    {
      "date": "2025年06月03日06:43",
      "link": "http://finance.people.com.cn/n1/2025/0603/c1004-40492453.html",
      "title": "当列车慢游成为新时尚"
    },
    {
      "date": "2025年06月03日05:57",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40492435.html",
      "title": "国际人士:中国一系列政策举措提振经济发展信心"
    },
    {
      "date": "2025年06月03日06:38",
      "link": "http://society.people.com.cn/n1/2025/0603/c1008-40492451.html",
      "title": "她走出大山,是为了回到大山"
    },
    {
      "date": "2025年06月03日06:32",
      "link": "http://society.people.com.cn/n1/2025/0603/c1008-40492480.html",
      "title": "民政部党组书记、部长:健全福利保障体系 增进困境儿童福祉"
    },
    {
      "date": "2025年06月03日06:35",
      "link": "http://politics.people.com.cn/n1/2025/0603/c1001-40492508.html",
      "title": "丘陵沟壑间刨出\"金疙瘩\""
    },
    {
      "date": "2025年06月03日07:20",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40492436.html",
      "title": "\"稳定\"和\"创新\"是观察中国发展的关键词"
    },
    {
      "date": "2025年06月03日13:58",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40493068.html",
      "title": "第四届中非经贸博览会吸引超2.8万人报名参加"
    },
    {
      "date": "2025年06月03日06:50",
      "link": "http://politics.people.com.cn/n1/2025/0603/c1001-40492493.html",
      "title": "山河显影|在白山黑水间吹响抗战号角"
    },
    {
      "date": "2025年06月03日10:55",
      "link": "http://ent.people.com.cn/n1/2025/0603/c1012-40492882.html",
      "title": "\"体育强国\"大家谈|落实学生每天运动2小时 办法总比困难多"
    },
    {
      "date": "2025年06月03日07:22",
      "link": "http://politics.people.com.cn/n1/2025/0603/c1001-40492510.html",
      "title": "蹊跷的社保"
    },
    {
      "date": "2025年06月03日10:55",
      "link": "http://ln.people.com.cn/n2/2025/0603/c378489-41247819.html",
      "title": "有回音|网友反映机动车不礼让行人 辽宁沈阳:确保全覆盖整治交通违法行为"
    },
    {
      "date": "2025年06月03日07:10",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40492421.html",
      "title": "俄乌第二轮直接谈判结束 同意交换阵亡士兵遗体"
    },
    {
      "date": "2025年06月03日05:59",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40492439.html",
      "title": "商务部新闻发言人就美方有关言论答记者问"
    },
    {
      "date": "2025年06月03日06:00",
      "link": "http://opinion.people.com.cn/n1/2025/0603/c1003-40492444.html",
      "title": "有卡通形象就能算是\"儿童食品\"吗?"
    },
    {
      "date": "2025年06月03日06:37",
      "link": "http://world.people.com.cn/n1/2025/0603/c1002-40492438.html",
      "title": "\"深化中亚国家和中国人民的友谊\""
    }
  ],
  "message": "获取成功"
}
```
