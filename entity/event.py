from dataclasses import dataclass
from datetime import timedelta, datetime
from hashlib import md5


@dataclass
class CourseEvent:
    day: int
    courseName: str
    className: str
    classroomName: str
    startTimeID: int
    endTimeID: int
    startTime: timedelta
    endTime: timedelta
    teacherName: str
    studentCount: int
    weeks: list[int]

    def identify(self) -> str:
        s = ""
        s += str(self.day)
        s += self.courseName
        s += self.className
        s += self.classroomName
        s += str(self.startTimeID)
        s += str(self.endTimeID)
        s += self.teacherName
        s += str(self.studentCount)
        return md5(s.encode("utf-8")).hexdigest()

    def merge(self, other: "CourseEvent"):
        if self.identify() != other.identify():
            raise Exception("Cannot merge different events")
        self.weeks.extend(other.weeks)
        self.weeks.sort()

    @property
    def period_str(self):
        if self.startTimeID != self.endTimeID:
            return f"第 {self.startTimeID} - {self.endTimeID} 节\r\n"
        else:
            return f"第 {self.startTimeID} 节\r\n"

    @property
    def classroom_str(self):
        if self.classroomName != "":
            return f'教室： {self.classroomName}\r\n'
        else:
            return ""

    @property
    def cycle_str(self):
        if len(self.weeks) == 1:
            return str(self.weeks[0])
        else:
            result = []
            start = self.weeks[0]
            for i in range(1, len(self.weeks)):
                if self.weeks[i] != self.weeks[i - 1] + 1:
                    if start == self.weeks[i - 1]:
                        result.append(start)
                    else:
                        result.append((start, self.weeks[i - 1]))
                    start = self.weeks[i]
            if start == self.weeks[-1]:
                result.append(start)
            else:
                result.append((start, self.weeks[-1]))

            def has_tuple(iterable):
                for element in iterable:
                    if isinstance(element, tuple):
                        return True
                return False

            def all_odd(iterable):
                for element in iterable:
                    if element % 2 == 0:
                        return False
                return True

            def all_even(iterable):
                for element in iterable:
                    if element % 2 == 1:
                        return False
                return True

            if not has_tuple(result):
                if all_odd(result):
                    return f"{result[0]} - {result[-1]} 单"
                elif all_even(result):
                    return f"{result[0]} - {result[-1]} 双"
                else:
                    s = ""
                    for _, v in enumerate(result):
                        s += f"{v}; "
                    return s[:-2]
            else:
                s = ""
                for _, v in enumerate(result):
                    if isinstance(v, tuple):
                        s += f"{v[0]} - {v[1]}; "
                    else:
                        s += f"{v}; "
                return s[:-2]

    def rrule(self, semester_start_time: datetime):
        week_base = semester_start_time.isocalendar().week - 1
        day_map = {
            1: "MO",
            2: "TU",
            3: "WE",
            4: "TH",
            5: "FR",
            6: "SA",
            7: "SU"
        }

        if len(self.weeks) == 1:
            return None
        else:
            return {
                "freq": "WEEKLY",
                "byday": day_map[self.day],
                "byweekno": list(map(lambda x: x + week_base, self.weeks)),
                "count": len(self.weeks)
            }
