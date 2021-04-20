# CalenderGenerator
一个用于生成井冈山大学的`ical格式`课表的`python程序`

> 参考了 `AC Better` 的[cqut-lesson-timetable-to-calendar](https://github.com/acbetter/cqut-lesson-timetable-to-calendar)

## 使用方法

需要 `Python ^3.8` 版本

执行 `pip[3] install -r requirements.txt` 来安装依赖

重命名 `info.py.example` 为 `info.py`

随后可以执行

```
python[3] curriculum.py
python[3] examArrangement.py
```

来生成课表和考试安排的 `ics文件` 

需要注意，这两个脚本都会输出生成的 `ics文件` 到 `output.ics`，执行第二个命令前需要先将已经生成的文件移动或重命名
