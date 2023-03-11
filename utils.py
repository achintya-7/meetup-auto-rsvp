import json

def get_headers(file: str) -> dict:
    with open('headers/'+file+'.json','r') as f:
        return json.loads(f.read())
    
def get_cookies(file: str) -> dict:
    with open('cookies/'+file+'.json','r') as f:
        return json.loads(f.read())

def find_token(html: str) -> str:
    pos=html.find("token")
    start=(html[pos:]).find('value="')+pos
    end=(html[start+7:]).find('"')+start+7
    return html[start+7:end]

def get_json(file: str) -> dict:
    with open(file,'r') as f:
        return json.loads(f.read())
    
def getUrl(group: str):
     return 'https://www.meetup.com/' + group + '/'