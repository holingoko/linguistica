import datetime

now = datetime.datetime.now().timetuple()
day = now.tm_yday
year = now.tm_year
end_day = datetime.datetime(year, 12, 31).timetuple().tm_yday
end_year = 2045

prefix = "{}_{}".format(end_year - year - 1, end_day - day)
