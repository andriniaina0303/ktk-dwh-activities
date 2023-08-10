from config.config import developpement as env_dev, production as env_prod
from models.Events import Events

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

run_paused_bounces()
 
# run_events_activities()