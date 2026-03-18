from .api import api
import json
from webuntis.utils.remote import rpc_request

def fetchHomeworks(start, end):
    session = api.login()

    jsessionid = session.config["jsessionid"]
    useragent = session.config["useragent"]
    server = session.config["server"]
    school = session.config["school"]

    s = session.config["_http_session"]

    url = server + "/WebUntis/api/homeworks/lessons?startDate=" + start.strftime("%Y%m%d") + "&endDate=" + end.strftime("%Y%m%d") + "&school=" + school

    print(url)

    headers = {
        u'User-Agent': useragent,
        u'Content-Type': u'application/json'
    }
    headers['Cookie'] = u'JSESSIONID=' + jsessionid

    r = s.get(url, data=json.dumps({}), headers=headers)
    result = r.text

    print(result)

    parameters = session._create_date_param(end, start, id=5, type="student")
    data = rpc_request(session.config, "getHomework", parameters)
    print(data)

    session.logout()

