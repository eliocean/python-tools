import datetime


def getEveryDay(begin_date, end_date):
    # 前闭后闭[begin_date,end_date]
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


if __name__ == '__main__':
    day_list = getEveryDay('2021-11-14', '2021-12-29')
    print("\n".join(day_list))
