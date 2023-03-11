from datetime import date
import requests

from utils import *

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
        if memberId:
            return memberId
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

if __name__ == '__main__':
    # memberId = login()
    # print(memberId)

    groups = get_json('groups.json')
    for group in groups['groups']:
        print("Getting events for " + group['name'])
        events = get_events(group['name'], group['end_date'])

        if events is None:
            print("\tNo events found")
            break

        print("\tFound " + str(len(events)) + " events")
        for event in events:
                print("\t\t" + event['name'])