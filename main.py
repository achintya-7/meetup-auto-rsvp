from datetime import date
import requests

from utils import *

def login2():
    user = get_json('credentials.json')
    headers = get_headers('login')
    # r = requests.get('https://secure.meetup.com/login/', headers=headers)

    headers = get_headers('login')
    # cookies = get_cookies('login')

    data = {
            'email': user['email'],
            'password': user['password'],
            'rememberme': 'on',
            'submitButton': 'Log in',
            'returnUri': 'https://www.meetup.com/',
            'op': 'login',
            'apiAppClientId': ''
        }
    loginResponse = requests.post('https://secure.meetup.com/login/', data=data)

    print(loginResponse.cookies)
     

def login():
    user = get_json('credentials.json')
    headers = get_headers('login')
    r = requests.get('https://secure.meetup.com/login/', headers=headers)

    headers = get_headers('login')
    cookies = get_cookies('login')

    data = {
        'operationName': 'login',
        'variables': {
            'input': {
                'email': user['email'],
                'password': user['password'],
                'rememberMe': False,
            },
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': '27c2dcd3fe18741b545abf6918eb37aee203463028503aa8b2b959dc1c7aa007',
            },
        },
    }

    try:
        loginResponse = requests.post('https://www.meetup.com/gql', headers=headers, json=data, cookies=cookies)
        loginJson = loginResponse.json()
        memberId = loginJson['data']['login']['memberId']
        return memberId, loginResponse.cookies
    except Exception as e:
        print(e)

def get_events(group: str, endDate: str):       
        startDate = str(date.today())
        requests.headers = get_headers('standard')
        requests.headers['referer'] = getUrl(group) + 'events/calendar/'
        requests.headers['x-meetup-activity'] = 'standardized_url=%2Furlname%2Fevents%2Fcalendar%2Fdate&standardized_referer=%2Furlname%2Fevents'

        queryStr = '(endpoint:members/self,meta:(method:get),params:(fields:\'memberships, privacy\'),ref:self,type:member),(endpoint:noop,flags:!(facebook_login_active,feature_microtargets_MUP-16377,nwp_event_template_MUP-16782,wework-announce,feature_google_tag_manager_MUP-19169),meta:(metaRequestHeaders:!(unread-notifications,unread-messages,admin-privileges,tos-query,facebook-auth-url,google-auth-url),method:get),params:(),ref:headers,type:headers),' + \
                   '(endpoint:' + group + ',meta:(flags:!(feature_app_banner_MUP-16415,feature_new_group_event_home_MUP-16376,feature_new_group_home_sharing_MUP-16516,feature_twitter_group_sharing_MW-2381),method:get),params:(country:in,fields:\'category,city_link,fee_options,join_info,leads,localized_location,membership_dues,member_sample,other_services,past_event_count,draft_event_count,proposed_event_count,pending_members,photo_count,photo_sample,photo_gradient,plain_text_description,plain_text_no_images_description,profile,self,topics,nominated_member,nomination_acceptable,member_limit,leader_limit,last_event,welcome_message,pro_rsvp_survey\',state:\'\'),ref:group,type:group),' + \
                   '(endpoint:' + group + '/events,list:' \
                   + '(dynamicRef:\'list_events_for_period_' + group + "_" + startDate + 'T00:00:00.000_' + endDate + 'T00:00:00.000\'),meta:(method:get),params:(fields:\'comment_count,event_hosts,featured_photo,plain_text_no_images_description,series,self,rsvp_rules,rsvp_sample,venue,venue_visibility\',' \
                   + 'no_earlier_than:\'' + startDate + 'T00:00:00.000\',' \
                   + 'no_later_than:\'' + endDate + 'T00:00:00.000\',status:\'past,cancelled,upcoming\'),ref:\'' \
                   + 'events_for_period_' + group + "_" + startDate + 'T00:00:00.000_' + endDate + 'T00:00:00.000\')'

        params = (
            ('queries', queryStr),
        )

        response = requests.get('https://www.meetup.com/mu_api/urlname/events/calendar/date', params=params)
        response = json.loads(response.text)
        name = response['responses'][2]['value']['name']
        events = response['responses'][3]['value']
        events.sort(key=lambda event: event['created'], reverse=True)  # Reverse sorting via date of creation

        return events

def rsvp_events(event_id: str, member_id: str, authCookies: dict):
    cookies = get_cookies('rsvp')
    cookies.update(authCookies)
    cookies.update({member_id: member_id})

    headers = get_headers('rsvp')

    json_data = {
        'operationName': 'rsvpToEvent',
        'variables': {
            'input': {
                'eventId': event_id,
                'response': 'YES',
                'proEmailShareOptin': False,
            },
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': '548c5377e0e656217cc0370fe7bd3fcf18dff95f0f7baedea20aa8031595f637',
            },
        },
    }

    response = requests.post('https://www.meetup.com/gql', cookies=cookies, headers=headers, json=json_data)
    print(response.text)


# def rsvp(group_name: str, event_id: str):
#     requests.headers = get_headers('standard')

#     requests.headers = {
#         'authority': 'www.meetup.com',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
#                         'Chrome/80.0.3987.132 Safari/537.36',
#         'sec-fetch-dest': 'document',
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
#                     'application/signed-exchange;v=b3;q=0.9',
#         'sec-fetch-site': 'none',
#         'sec-fetch-mode': 'navigate',
#         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#     }

#     params = (
#         ('action', 'rsvp'),
#         ('response', 'yes'),
#     )

#     url = getEventUrl(group=group_name, eventId=event_id)

#     response = requests.get(url, params=params)
#     if response.status_code != 200:
#         print('Failed to get event page')
#         return

#     referer = url + '?action=rsvp&response=yes'  # referer in header
#     requests.headers = get_headers('rsvp')
#     requests.headers['referer'] = referer
#     # requests.headers['x-mwp-csrf'] = requests.cookies['x-mwp-csrf-header']
#     queryStr = '(endpoint:' \
#                 + group_name + "/events/" + event_id + "/rsvps" \
#                 + ',meta:(method:post),' \
#                 + 'params:(eventId:' + event_id \
#                 + ',fields:rsvp_counts,' \
#                 + 'response:yes,' \
#                 + 'self.group.urlname:' +group_name + ')' \
#                 + ',ref:rsvpAction' + "_" + group_name + '_' + event_id + ')'

#     data = {
#         'queries': queryStr
#     }
#     response = requests.post('https://www.meetup.com/mu_api/urlname/events/eventId', data=data)
#     print(response.text)

if __name__ == '__main__':
    memberId, cookies = login()
    print(cookies)

    groups = get_json('groups.json')
    for group in groups['groups']:
        print("Getting events for " + group['name'])
        events = get_events(group['name'], group['end_date'])

        if len(events) == 0:
            print("\tNo events found")
            continue

        print("\tFound " + str(len(events)) + " events")

        for event in events:
            print(event['name'])
            rsvp_events(event['id'], memberId, cookies)



        