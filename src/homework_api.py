from .api import api
import json

def fetchHomeworks(start, end):
    session = api.login()

    jsessionid = session.config["jsessionid"]
    useragent = session.config["useragent"]
    server = session.config["server"]
    school = session.config["school"]

    session = session.config["_http_session"]

    url = server + "/WebUntis/api/homeworks/lessons?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d") + "&school=" + school

    print(url)

    headers = {
        u'User-Agent': useragent,
        u'Content-Type': u'application/json'
    }
    headers['Cookie'] = u'JSESSIONID=' + jsessionid

    r = session.get(url, data=json.dumps({}), headers=headers)
    result = r.text

    print(result)

    session.logout()
