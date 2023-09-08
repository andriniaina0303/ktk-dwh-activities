from config.config import developpement as env_dev, production as env_prod
from models.Events import Events
import time,threading
from datetime import datetime

env = env_prod


def run_events_activities():
    try:
        events = Events(confDb=env.CONFIG_DATABASE, events=env.LISTE_EVENTS,tmpFolder=env.TMP_FOLDER,es_access=env.ES_ACCESS, sftp=env.SFTP_ACCESS,pauseBouncesCampaign=False)
        events.start_process(config_file=env.CONFIG_FILE)
    except Exception as e:
        print('error at run events process ',e)
        pass
    
def run_paused_bounces():
    try:
        events = Events(confDb=env.CONFIG_DATABASE, events=env.BOUNCES_EVENTS,tmpFolder=env.TMP_FOLDER,es_access=env.ES_ACCESS, sftp=env.SFTP_ACCESS,pauseBouncesCampaign=True)
        events.start_process(config_file=env.CONFIG_FILE)
    except Exception as e:
        print('error at run bounces process ',e)
        pass
    
def run_sendable_lists():
    try:
        events = Events(confDb=env.CONFIG_DATABASE, events=env.LISTE_EVENTS,tmpFolder=env.TMP_FOLDER,es_access=env.ES_ACCESS, sftp=env.SFTP_ACCESS_SEGMENT,pauseBouncesCampaign=False)
        events.start_process_segments_all(config_file=env.CONFIG_FILE)
    except Exception as e:
        print('error at run segments process ',e)
        pass
       
def run_activities_export():
    date_process = []
    while True:
        start = datetime.now()
        verif = str(datetime.now()).split(' ')[0]
        ########### setting condition : building sendable lists only each saturday between 10am an 3pm
        if start.weekday() == 5 and  start.time() >= datetime.time(0, 1) and start.time() <= datetime.time(16, 0) and verif not in date_process:
            try:
                run_sendable_lists()
            except Exception as e:
                #send email notification for failed process
                pass
            date_process.append(verif)
        else:
            try:
                run_events_activities()
                end = datetime.now()
                duration = end -start
                with open('log_time_activities.txt','a') as fic:
                    fic.write(f'Task start at {start} and finished at {end}, duration: {duration} \n')
                print(f"Task done => {duration}")
                time.sleep(1800)
            except Exception as e:
                #send email notification for failed process
                pass

def run_check_blocked_campagnes():
    while True:
        run_paused_bounces()
        time.sleep(10)


## thread_blocked = threading.Thread(target=run_check_blocked_campagnes)
# thread_activities = threading.Thread(target=run_activities_export)
# thread_activities.start()

run_sendable_lists()