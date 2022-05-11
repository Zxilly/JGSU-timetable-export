from dataclasses import dataclass
from datetime import timedelta
from hashlib import md5


@dataclass
class CourseEvent:
    day: int
    courseName: str
    className: str
    classroomName: str
    startTimeID: str
    endTimeID: str
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
        s += self.startTimeID
        s += self.endTimeID
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
            result = ""
            start = self.weeks[0]
            for i in range(1, len(self.weeks)):
                if self.weeks[i] != self.weeks[i - 1] + 1:
                    result += f"{start}-{self.weeks[i - 1]}, "
                    start = self.weeks[i]
            result += f"{start}-{self.weeks[-1]}"
            return result
