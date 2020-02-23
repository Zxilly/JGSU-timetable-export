import icalendar
import datetime
from info import *


def rmzero(input):
    return int(str(input))


def getcalender(course):
    calt = icalendar.Calendar()
    calt['version'] = '2.0'
    calt['prodid'] = '-//Zxilly//JGSUCalender//CN'


