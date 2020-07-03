from secrets import consumer_key, access_token, ifttt_key
import sched
import time
import requests

class PeriodicScheduler(object):
    """ schedule task to run every X seconds """
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def setup(self, interval, action, actionargs=()):
        """ main loop """
        action(*actionargs)
        self.scheduler.enter(interval, 1, self.setup, (interval, action, actionargs))

    def run(self):
        """ initiate scheduler """
        self.scheduler.run()

# The main event to execute
def periodic_event():
    """ fetch list of archived articles from pockets
    if the article contains highlights, then push to IFTTT
    """
    # print('fetched: ' + str(int(time.time())))
    latest = time.time() - INTERVAL
    params = {
        'annotations': 1,
        'total': 1,
        'forceaccount': 1,
        'state': 'archive',
        'sort': 'newest',
        'detailType': 'complete',
        'since': latest,
        'consumer_key': consumer_key,
        'access_token': access_token
    }

    retrieve_url = 'https://getpocket.com/v3/get'

    result = requests.get(
        url=retrieve_url,
        params=params
    )

    try:
        articles = result.json()['list']
        for _, value in articles.items():
            if 'annotations' in value:
                print('===========')
                print('fetched: ' + str(int(time.time())))
                print('+++' + value['given_title'] + '+++')

                pocket_url = 'https://app.getpocket.com/read/'+value['resolved_id']
                print('URL: '+pocket_url)
                print(value['given_url'])
                print()
                highlights = ''
                for annotation in value['annotations']:
                    print(annotation['quote'])
                    highlights += '<p>' + annotation['quote'] + '</p>'
                    print('')

                payload = {
                    'value1' : value['given_title'],
                    'value2' : '<p>URL: '+pocket_url+'</p><p>'+value['given_url']+'</p>'+highlights
                }
                url = 'https://maker.ifttt.com/trigger/new_notes/with/key/'+ifttt_key
                requests.post(url=url, data=payload)

    except:
        pass

    latest = time.time()


INTERVAL = 5 # every 5 second
periodic_scheduler = PeriodicScheduler()
periodic_scheduler.setup(INTERVAL, periodic_event) # it executes the event just once
periodic_scheduler.run() # it starts the scheduler 
