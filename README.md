# CalenderGenerator
一个用于生成井冈山大学的`ical格式`课表的`python程序`

> 参考了 `AC Better` 的[cqut-lesson-timetable-to-calendar](https://github.com/acbetter/cqut-lesson-timetable-to-calendar)

## 在线生成

访问 `https://ical.learningman.top/docs`

使用 `refresh` 方法刷新考试或课程的缓存，返回生成的 `ical` 文件的 `url`

## 使用方法

需要 `Python ^3.8` 版本

执行 `pip[3] install -r requirements.txt` 来安装依赖

重命名 `info.example.py` 为 `info.py` 并填入 cookies

> 可以访问 `https://vpn2.jgsu.edu.cn/enlink/sso/login/` 进入教务系统，随后访问 document.cookie 获取 cookie 字符串

随后可以执行

```
python[3] curriculum.py
python[3] examArrangement.py
```

来生成课表和考试安排的 `ics文件` 
