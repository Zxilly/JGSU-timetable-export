def display(cal):
    return cal.to_ical().decode('utf-8').replace('\r\n','\n').strip()

def print_cal(cal):
    print(cal.to_ical())