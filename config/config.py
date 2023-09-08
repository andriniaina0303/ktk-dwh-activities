

class developpement(object):
    ######## database config ##################
    CONFIG_DATABASE = {'user': 'root', 'password': 'root', 'host': 'localhost',  'database': 'konticrea_v3','raw': True}
    CONFIG_FILE = "config/all-task-prod.xlsx"
    LISTE_EVENTS = [
        {"events": "Clicks", "endname": "_clicks_report.csv"},
        {"events": "Bounces", "endname": "_bounces_report.csv"},
        {"events": "Complaints", "endname": "_complaints_report.csv"},
        {"events": "Subscriptions", "endname": "_subscriptions_report.csv"},
        {"events": "Removals", "endname": "_unsubscriptions_report.csv"},
        {"events": "Opens", "endname": "_opens_report.csv"},
        {"events": "Sends", "endname": "_sends_report.csv"},
    ]
    BOUNCES_EVENTS = [{"events": "Bounces", "endname": "_bounces_report.csv"}]
    TMP_FOLDER = 'temp/'
    ES_ACCESS = {
        "login" : "landykontiki@gmail.com",
        2 : "s041@02Fv*/2020",
        3 : "nGjD@25ssEg*/",
        4 : "6BhJB@15AHM*/",
        5 : "qyp@15OhcrS*/",
        6 : "OyMM@15Lu92*/",
        7 : "c5oW*oS5*/",
        8 : "E#gb0Ka1"
    }
    SFTP_ACCESS = {
        "sftphost": "sftp2.kontikimedia.com",
        "sftpuser": "activitydwh",
        "sftppassword": "aBi3&31qGqhY",
        "sftppath": "/ftp_up/test_andre/"
    }
    SFTP_ACCESS_SEGMENT = {
        "sftphost": "sftp2.kontikimedia.com",
        "sftpuser": "segmentsdwh",
        "sftppassword": "H!d6p55oKjlF",
        "sftppath": "/ftp_up/test/"
    }
    
class production(object):
    ######## database config ##################
    CONFIG_DATABASE = {'host': '192.168.1.2', 'user': 'konticrea', 'database': 'konticrea_v2', 'password': 'Ya7nC3uQ3', 'raw': True}
    CONFIG_FILE = "config/all-task-prod.xlsx"
    LISTE_EVENTS = [
        {"events": "Clicks", "endname": "_clicks_report.csv"},
        {"events": "Bounces", "endname": "_bounces_report.csv"},
        {"events": "Complaints", "endname": "_complaints_report.csv"},
        {"events": "Subscriptions", "endname": "_subscriptions_report.csv"},
        {"events": "Removals", "endname": "_unsubscriptions_report.csv"},
        {"events": "Opens", "endname": "_opens_report.csv"},
        {"events": "Sends", "endname": "_sends_report.csv"},
    ]
    BOUNCES_EVENTS = [{"events": "Bounces", "endname": "_bounces_report.csv"}]
    TMP_FOLDER = 'temp/'
    ES_ACCESS = {
        "login" : "landykontiki@gmail.com",
        2 : "s041@02Fv*/2020",
        3 : "nGjD@25ssEg*/",
        4 : "6BhJB@15AHM*/",
        5 : "qyp@15OhcrS*/",
        6 : "OyMM@15Lu92*/",
        7 : "c5oW*oS5*/",
        8 : "E#gb0Ka1"
    }
    SFTP_ACCESS = {
        "sftphost": "sftp2.kontikimedia.com",
        "sftpuser": "activitydwh",
        "sftppassword": "aBi3&31qGqhY",
        "sftppath": "/ftp_up/test_andre/"
    }
    SFTP_ACCESS_SEGMENT = {
        "sftphost": "sftp2.kontikimedia.com",
        "sftpuser": "segmentsdwh",
        "sftppassword": "H!d6p55oKjlF",
        "sftppath": "/ftp_up/"
    }