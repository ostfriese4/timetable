from .api import api

def fetchHomeworks(start, end):
    api.login()
    session = api.session

    jsessionid = session.config["jsessionid"]
    useragent = session.config["useragent"]
    server = session.config["server"]

    url = server + "/WebUntis/api/homeworks/lessons?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d")
    print(url)

    api.logout()
