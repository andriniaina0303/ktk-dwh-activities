from datetime import datetime,timedelta
import pandas as pd
import os, requests,time,hashlib, sys,zipfile,xmltodict, pysftp,warnings, threading
import mysql.connector as mysql
import http.client
import shutil
from bs4 import BeautifulSoup as bs
from models.Notification import Notification
import time
import progressbar

class Events(object):
    
    def __init__(self, confDb, events, tmpFolder, es_access,sftp,pauseBouncesCampaign=False):
        self.pauseBouncesCampaign = pauseBouncesCampaign
        self.es_access = es_access
        self.confDB = confDb
        self.events = events
        self.tmpFolder = tmpFolder
        self.sftp = sftp
        self.dateProcess = str(datetime.now()).split(' ')[0]
        # self.dateProcess = '2023-06-26'
        self.api_path_methods = 'Api/Activities'
        self.api_path_pause = 'Api/Newsletters/'
        self.pathLogFile = 'logs/'
        self.pathLogSegment = 'logs_segment/'
        
        self.pathLogPaused = 'logs_paused_campagne/'
        self.liste_tags = []
        self.blocked_indication = {
            #GMAIL
            "gmail.com": "smtp;550 5.7.1 [[ip_address] 19] Our system has detected that this message is likely suspicious due to the very low reputation of the sending domain. To best protect our users from spam, the message has been blocked. Please visit https://support.google.com/mail/answer/188131 for more information. [removed]",
            #yahoo
            "aol.fr" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "aol.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.fr" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "ymail.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.co.in" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "rocketmail.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "aim.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.co.uk" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.it" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.ar" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.ca" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.br" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.es" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.sg" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.de" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "netscape.net" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.mx" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "aol.co.uk" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.ro" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.be" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.co.id" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.cl" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.ph" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.co.nz" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.tw" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.com.vn" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.in" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "yahoo.pl" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "rogers.com" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "aol.de" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            "verizon.net" : "smtp;421 4.7.0 [TSS04] Messages from [ip_address] temporarily deferred due to unexpected volume or user complaints - [ip_address]; see https://postmaster.yahooinc.com/error-codes",
            #outlook
            "50pas972.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "aces-sobesky.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "acfci.cci.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "achard-sa.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "actemium.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "actes-sud.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "adecco.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "adisseo.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "advanta.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "aforp.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "agss.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "akanea.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "altareacogedim.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "alvs.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ampvisualtv.tv" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "arcadie-so.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "arminaeurope.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "aviapartner.aero" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "belambra.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "betchoulet.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "bms.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "bouyguestelecom.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cabinet-taboni.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cegelec.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cegid.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cern.ch" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cerp-rouen.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cfa-afmae.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cfecgc.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ch-wasquehal.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "chateauform.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cheval-sa.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "chinasealeh.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "chpolansky.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cneap.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cokecce.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "conair.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "cr-champagne-ardenne.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "creativenetwork.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "croissy.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "daher.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "darty.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "dartybox.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "davines.it" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "dbmail.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "delachaux.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "desenfans.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "drancy.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ece-france.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ecole-eme.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "edhec.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "edhec.edu" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "edu.esce.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "effem.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "egidys.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ehtp.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "eiffage.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "esatea.net" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "esc-larochelle.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "esc-pau.net" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "esitc-caen.net" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "et.esiea.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ets-bernard.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ets-verhaeghe.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "etu.u-pec.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "eurocast.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "evun360.onmicrosoft.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "expanscience.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "expertiscfe.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "fft.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "fidel-fillaud.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "fr.tmp.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "france-boissons.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "gacd.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "gfi.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "gl-events.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "gondrand.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "goodyear.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "grandhainaut.cci.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "grandlebrun.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "grassavoye.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "groupe-crit.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "groupeflo.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "groupeisf.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "haut-rhin.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hoparb.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.be" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.ca" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.ch" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.co.kr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.co.uk" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.com.tr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.de" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.es" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.gr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "hotmail.it" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "icfenvironnement.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "immodefrance.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "inseec-france.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "inseec.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ipag.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ipsen.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ipsos.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "isipharm.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "jcdava.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "joffeassocies.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "kedgebs.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lamutuellegenerale.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lesbougiesdefrance.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lespinet.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lgh.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.be" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.ca" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.co.uk" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.com.pt" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.ie" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.it" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "live.ru" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "loca-rhone.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lorraine.eu" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "lyonnaise-des-eaux.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "mairie-villeparisis.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "majencia.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "marie-laure-plv.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "marquant.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "marseille.archi.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "materne.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "mdlz.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "medecinsdumonde.net" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "meylan.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "micheldechabannes.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "milan.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "mondadori.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "monitorgd.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "monitoroffice365.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "monoprix.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "montpellier-bs.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "msn.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "opcapl.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "oppbtp.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "outlook.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "outlook.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "pagesjaunes.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "pathe.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "planet-fitness.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "pommier.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ponticelli.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "prepacom.net" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "previfrance.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "purina.nestle.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "quimper.cci.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "redoute.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "rexel.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "rumeurpublique.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "sadoul.biz" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "scam.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "scgpm.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "shqiptar.eu" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "sita.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "skema.edu" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "socotec.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "sofinther.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "spiebatignolles.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "staci.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "starlight.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "steria.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "supdepub.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "supinfo.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "suzuki.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "synergie.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "synhorcat.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "taz-media.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "tessi.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "tf1.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "tgh82.org" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "tnb.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "toutelectric.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "tso-catenaires.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ucem.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "umusic.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "unifrance.org" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "vertbaudet.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "vet-alfort.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "viacesi.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ville-bastia.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ville-lebourget.fr" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "vinci-energies.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "wartsila.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "windowslive.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            "ynov.com" : "x-pmta;bounce-queue;reply:550 5.7.1 Unfortunately, messages from [[ip_address]] weren't sent. Please contact your Internet service provider since part of their network is on our block list (S3150). You can also refer your provider to http://mail.live.com/mail/troubleshooting.aspx#errors. [[removed]]",
            #Bouygues
            "bbox.fr" : "smtp;554 5.7.1 Rejected for policy reason",
            #apple
            "icloud.com" : "smtp;550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "me.com" : "smtp;550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "mac.com" : "smtp;550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "canal-plus.com": "smtp;554 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "synergie.fr": "smtp;554 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            #free
            "free.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "libertysurf.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "infonie.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "chez.com" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "aliceadsl.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "freesbee.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "worldonline.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "online.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "alicepro.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            "nomade.fr" : "smtp;421 Too many spams from your IP ([ip_address]), please visit http://postmaster.free.fr/",
            #sfr
            "9business.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "9online.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "akeonet.com" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "cario.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "cegetel.net" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "club-internet.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "club.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "clubinternet.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "estvideo.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "fnac.net" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "mageos.com" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "modulonet.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "neuf.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "noos.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "numericable.com" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "numericable.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "sfr.fr" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            "waika9.com" : "smtp;550 5.7.1 Email 4RH2xT4NwZz1LQKck rejected per SPAM policy",
            #laposte
            "laposte.net": "smtp;550 5.7.1 Service refuse. Veuillez essayer plus tard. service refused, please try later. LPN007_510",
            #orange
            "orange.fr" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            "wanadoo.fr" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            "martinetelec.com" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            "elsil.fr" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            "cabinetcourty.com" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            "stebdx.fr" : "smtp;421 [removed] Service refuse. Veuillez essayer plus tard. Service refused, please try later. OFR_999 [999]",
            #telephonica
            "telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "movistar.es" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "iies.es" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "rcmadrid.c.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "aplevante.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "adgase.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "inmobiliariamatias.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "10grandur.infonegocio.com" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "masterfon.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "verdu48.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "gesmac.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "diazpan.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "grossen.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "macarmen.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "dentalreyes.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "laymi.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "luar.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "jagsegade.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "e12.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "elenarana.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "enzler.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "fida.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "muguruza.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "adihuesca.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "perrino.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            "delio.e.telefonica.net" : "smtp;554 5.7.1 Service unavailable; Client host [[ip_address]] blocked using sbl-xbl.spamhaus.org; https://www.spamhaus.org/sbl/query/SBLCSS",
            #Telecom Italia
            "alice.it" : "smtp; 550 5.7.1 Mail from IP [ip_address] was rejected due to listing in Spamhaus SBL. For details please see http://www.spamhaus.org/query/bl?ip=[ip_address]",
            "tin.it" : "smtp; 550 5.7.1 Mail from IP [ip_address] was rejected due to listing in Spamhaus SBL. For details please see http://www.spamhaus.org/query/bl?ip=[ip_address]",
            "aliceposta.it" : "smtp; 550 5.7.1 Mail from IP [ip_address] was rejected due to listing in Spamhaus SBL. For details please see http://www.spamhaus.org/query/bl?ip=[ip_address]",
            "tim.it" : "smtp; 550 5.7.1 Mail from IP [ip_address] was rejected due to listing in Spamhaus SBL. For details please see http://www.spamhaus.org/query/bl?ip=[ip_address]",
            #Italiaonline
            "libero.it" : "smtp;550 smtp-13.iol.local smtp-13.iol.local IP blacklisted by CSI. For remediation please use http://csi.cloudmark.com/reset-request/?ip=[ip_address] [smtp-13.iol.local; LIB_102]",
            "virgilio.it" : "smtp;550 smtp-13.iol.local smtp-13.iol.local IP blacklisted by CSI. For remediation please use http://csi.cloudmark.com/reset-request/?ip=[ip_address] [smtp-13.iol.local; LIB_102]",
            #telstra
            "bigpond.com.au" : "smtp;550 smtp-13.iol.local smtp-13.iol.local IP blacklisted by CSI. For remediation please use http://csi.cloudmark.com/reset-request/?ip=[ip_address] [smtp-13.iol.local; LIB_102]",
            "telstra.com" : "smtp;550 smtp-13.iol.local smtp-13.iol.local IP blacklisted by CSI. For remediation please use http://csi.cloudmark.com/reset-request/?ip=[ip_address] [smtp-13.iol.local; LIB_102]",
            "msn.com.au" : "smtp;550 smtp-13.iol.local smtp-13.iol.local IP blacklisted by CSI. For remediation please use http://csi.cloudmark.com/reset-request/?ip=[ip_address] [smtp-13.iol.local; LIB_102]",
            #optus
            "optusnet.com.au" : "smtp;521 5.7.1 <[email_address]>: Recipient address rejected: You are not allowed to send mail. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] if you feel this is in error.",
            "optusnet.com" : "smtp;521 5.7.1 <[email_address]>: Recipient address rejected: You are not allowed to send mail. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] if you feel this is in error.",
            "optus.net" : "smtp;521 5.7.1 <[email_address]>: Recipient address rejected: You are not allowed to send mail. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] if you feel this is in error.",
            #iinet
            "iinet.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "westnet.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "ozemail.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "adam.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "netspace.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "wn.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "smartchat.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "iinet.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "ihug.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "senet.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "powerup.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "iimetro.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "vtown.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "hn.ozemail.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "bigblue.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "decostar.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "froggy.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "computerconsulting.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "myplace.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "printingideas.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "openaccess.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "upnaway.com" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "a1.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "ctcinsul.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "esoft.com.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "agn.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            "netc.net.au" : "smtp;554 irony-in31.icp.iinet.net.au Your access to this mail system from [ip_address] has been rejected due to the sending MTA's poor reputation. If you believe that this failure is in error, please contact the intended recipient via alternate means.",
            #zigoo
            "ziggo.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "home.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "upcmail.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "chello.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "casema.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "quicknet.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "zeggis.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "zinders.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "blueyonder.co.uk" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "razcall.nl" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            "virginmedia.com" : "smtp;550 mx10.tb.mail.iss.as9143.net mx10.tb.mail.iss.as9143.net MXIN103 Your IP [ip_address] is in RBL. Please see http://csi.cloudmark.com/reset-request/?ip=[ip_address] ;id=HL3DqIsJDuQYf;sid=HL3DqIsJDuQYf;mta=mx10.tb;d=20230706;t=111323[CET];ipsrc=[ip_address];",
            #tele2
            "webedia-group.com" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "bostonk12.org" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "detalententoren.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "opwaardz.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "schepelweyen.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "stuktvshop.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "vonken.com" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "bskopermolen.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "sebsoft.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "mozaiek.scodelft.nl" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "obsdespringplank.net" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            "zalando-lounge.be" : "smtp;550 A URL in this email (goededeal . com) is listed on https://spamrl.com/. Please resolve and retry",
            #talktalk
            "onetel.com": "smtp; 550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            #Virgin media
            "virginmedia.com" : "@me.com; 550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "blueyonder.co.uk" : "@me.com; 550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
            "virgin.net" : "@me.com; 550 5.7.0 Blocked - see https://ipcheck.proofpoint.com/?ip=[ip_address]",
        }
        self.log_events = False
        self.connection = None
        self.cursor = None
        self.messageContentId = []
        self.waiting_delay = 60
        self.temp_sl = "temp_sl/"
        self.myconfig_sl = []
        warnings.filterwarnings("ignore", module="pysftp")
    
    def start_process(self, config_file):
        logs_directory = os.path.join(self.pathLogFile, self.dateProcess)
        try:
            os.mkdir(logs_directory)
        except Exception as e:
            pass
        logs_file = os.path.join(logs_directory, str(datetime.now()))
        if self.log_events :
            sys.stdout = open(logs_file +'.txt','a')
        self.getListTagsStats()
        try:
            df = pd.read_excel(config_file)
            liste_service_2 = []
            liste_service_3 = []
            liste_service_4 = []
            liste_service_5 = []
            liste_service_6 = []
            liste_service_7 = []
            liste_service_8 = []
            
            mytask = []
            mythread = []
            for i, row in df.iterrows():
                if int(row['activities']) == 1:
                    if int(row['service']) == 2:
                        liste_service_2.append(row)
                    if int(row['service']) == 3:
                        liste_service_3.append(row)
                    if int(row['service']) == 4:
                        liste_service_4.append(row)
                    if int(row['service']) == 5:
                        liste_service_5.append(row)
                    if int(row['service']) == 6:
                        liste_service_6.append(row)
                    if int(row['service']) == 7:
                        liste_service_7.append(row)
                    if int(row['service']) == 8:
                        liste_service_8.append(row)
            mytask.append(liste_service_2)
            mytask.append(liste_service_3)
            mytask.append(liste_service_4)
            mytask.append(liste_service_5)
            mytask.append(liste_service_6)
            mytask.append(liste_service_7)
            mytask.append(liste_service_8)
            
            for task in mytask:
                th = threading.Thread(target=self.make_process, args=[task])
                th.start()
                mythread.append(th)
                time.sleep(1)
                
                
            for thread in mythread:
                thread.join()
                
            if self.log_events :
                    sys.stdout.close()
                    sys.stdout = sys.__stdout__
                
        except Exception as e:
            print('error at start process ',e)
            pass
        
    def make_process(self, rows):
        try:
            for row in rows:
                # logs_directory = os.path.join(self.pathLogFile, row['acronyms'])
                # try:
                #     os.mkdir(logs_directory)
                # except Exception as e:
                #     pass
                # logs_file = os.path.join(logs_directory, str(datetime.now()).split(' ')[0])
                # if self.log_events :
                #     sys.stdout = open(logs_file +'.txt','a')
                timeStart = datetime.now()
                print(f'#####################{timeStart}###########################')
                path = str(row['dwh_id'])+'_'+self.dateProcess
                databaseFolder = os.path.join(self.tmpFolder, path)
                try:
                    os.mkdir(databaseFolder)
                except Exception as e:
                    pass
                for event in self.events:
                    print(event)
                    self.make_activity_export(events=event,path=databaseFolder,config_domain=row)
                
                if self.pauseBouncesCampaign is False:
                    self.zipper_directory(nom_dossier=databaseFolder, nom_zip= databaseFolder+'.zip')
                    self.uploadToSftp(databaseFolder+'.zip')
                    try:
                        os.remove(databaseFolder+'.zip')
                        shutil.rmtree(databaseFolder)
                    except Exception as e:
                        print(e)
                        pass
                end = datetime.now()
                print(f"Process start at {timeStart} and finished at {end}")
                print(f"Process take {datetime.now() - timeStart}")
                print(f'##############################################')
                # if self.log_events :
                #     sys.stdout.close()
                #     sys.stdout = sys.__stdout__
                
                
        except Exception as e:
            print('error at making process for each database ',e)
            pass
    
    def getListTagsStats(self):
        try:
            url = "https://stats.kontikimedia.com/publicapi/statsapi"
            apikey = "b48fac8d4d8bb8200896ca4c66ca0180"
            with requests.post(url + "/gettags", data={"userapikey": apikey}) as r:
                result = r.json()
            print('liste tags getted from api')
            self.liste_tags = result
        except Exception as e:
            print('error getting list tags ', e)
            pass    
    
    def downloadFile(self,url_events, path):
        try:
            filename = os.path.join(path, str(int(time.time())) + '.csv')
            response = requests.get(url_events)
            response.raise_for_status()
            data_res = response.text
            with open(filename, 'w', encoding="utf-8") as out:
                out.write(data_res)
            
            df = pd.read_csv(filename, encoding='utf-8', sep=',', dtype=str, engine='python')
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            df.to_csv(filename, encoding='utf-8', index=False)
            return filename
        except Exception as e:
            print('error downloading file from routeur', e)
            pass

    def getCampaignInfoFromId(self, info, message_id):
        elem = {}
        elem['status'] = None
        elem['advertiser'] = ''
        elem['client'] = ''
        elem['tags_id'] = ''  
        elem['messageId'] = message_id 
        try:
            if len(self.messageContentId) > 0:
                for item in self.messageContentId:
                    if int(item['messageId']) == int(message_id):
                        elem['status'] = "success"
                        elem['advertiser'] = item['advertiser']
                        elem['client'] = item['client']
                        elem['tags_id'] = item['tags_id']
                        break
            
            if elem['status'] is None:
                # connection = mysql.connect(user="konticrea", password="Ya7nC3uQ3", host="192.168.1.2", database='konticrea_v2')
                # connection = mysql.connect(user="root", password="root",host='localhost',database='konticrea_v3')
                connection = mysql.connect(** self.confDB)
                
                cursor = connection.cursor()
                query = f'SELECT id,advertiser,client,tags_id from creativities where base_id={str(int(info["ktk_id"]))} and router_id={str(message_id)}'
                cursor.execute(query)
                query_result = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in cursor.fetchall()]]
                cursor.close()
                connection.close()
                if len(query_result) > 0:
                    elem['status'] = 'success'
                    elem['advertiser'] = query_result[0]['advertiser']
                    elem['client'] = query_result[0]['client']
                    elem['tags_id'] = query_result[0]['tags_id']
                    elem['messageId'] = message_id
                    self.messageContentId.append(elem)
        except Exception as e:
            # print('error getting campagn info from database ',e)  
            pass
        finally:
            return  elem
       
    def getTagsName(self,tags_id):
        tagsname = ''
        if tags_id == '':
            pass
        else:
            try:
                for elem in self.liste_tags:
                    if int(elem['id']) == int(tags_id):
                        tagsname = elem['dwtag']
                        break
            except Exception as e:
                print('error ggetting tagname ', e)
                pass
        return tagsname
          
    def build_clicks(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            df['sid'] = [ x for x in df['MessageId']]
            df['reason'] = [ '' for x in df['MessageId']]
            df['diagnosticCode'] = [ '' for x in df['MessageId']]
            df['firstname'] = [ '' for x in df['MessageId']]
            df['lastname'] = [ '' for x in df['MessageId']]
            df['lists'] = [ '' for x in df['MessageId']]
            df['supressionlists'] = [ '' for x in df['MessageId']]
            df['fields'] = [ '' for x in df['MessageId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            df['tag'] = [ self.processTag(config, int(x)) for x in df['MessageId']]
            columns = ['datetime','email','reason','sid','tag','diagnosticCode','firstname','lastname','domain','lists','fields','supressionlists']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Clicks_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)
        except Exception as e:
            print('error building clicks ',e)
            pass
    
    def build_bounces(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            df['sid'] = [ x for x in df['MessageId']]
            df['reason'] = [ x for x in df['Reason']]
            # df['diagnosticCode'] = [ x.replace(';','_') if isinstance(x, str) else  '' for x in df['DiagnosticCode']]
            df['diagnosticCode'] = [ x  for x in df['DiagnosticCode']]
            
            df['firstname'] = [ '' for x in df['MessageId']]
            df['lastname'] = [ '' for x in df['MessageId']]
            df['lists'] = [ '' for x in df['MessageId']]
            df['supressionlists'] = [ '' for x in df['MessageId']]
            df['fields'] = [ '' for x in df['MessageId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            df['tag'] = [ self.processTag(config, int(x)) for x in df['MessageId']]
            
            if self.pauseBouncesCampaign:
                liste_campagne_to_stop = []
                my = []
                for i, row in df.iterrows():
                    domain = ((row['Email']).split('@'))[1]
                    if domain.strip() in self.blocked_indication:
                        if self.blocked_indication[domain] == row['diagnosticCode']:
                            status = True
                            for item in liste_campagne_to_stop:
                                if int(item['messageId']) == int(row["MessageId"]):
                                    my.append(item['messageId'])
                                    status = False
                                    break
                           
                            if status:
                                elem = {}
                                elem['messageId'] = row["MessageId"]
                                liste_campagne_to_stop.append(elem)
                                with open('bounces.txt','a',encoding="utf-8") as fic:
                                    fic.write(f'{row["MessageId"]} => {domain} => {row["diagnosticCode"]} \n')
                                row_dict = df.loc[i].to_dict()
                                self.stopSendouts(config=config, mydict=row_dict)
                                                            
            df['diagnosticCode'] = [ x.replace(';','_') if isinstance(x, str) else  '' for x in df['diagnosticCode']]              
            columns = ['datetime','email','reason','sid','tag','diagnosticCode','firstname','lastname','domain','lists','fields','supressionlists']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Bounces_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            
            os.remove(path_export_file)
            
            # df = pd.read_csv(path_export_file, low_memory=False)
            # listeTag = []
            # listeAdvertiser = []
            # listeAgency = []
            # listeMd5 = []
            # listeDiagnosticCode = []
            # listeDomain = []
            # listeFirstname = []
            # listeLastname = []
            # listeListes = []
            # listFields = []
            # listSuppressionLists = []
            # listeDate = []
            # listeMessageId = []
            # listeReason = []
            # liste_campagne_to_stop = []
            # for i, row in df.iterrows():
            #     additional_info = self.getCampaignInfoFromId(config, int(row['MessageId']))
            #     listeDate.append(row['Date'])
            #     listeMd5.append(hashlib.md5((row['Email']).encode()).hexdigest())
            #     listeTag.append(self.getTagsName(additional_info['tags_id']) if  additional_info['tags_id'] != '' else '')
            #     listeDomain.append(((row['Email']).split('@'))[1])
            #     listeAdvertiser.append(additional_info['advertiser'])
            #     listeAgency.append(additional_info['client'])
            #     code = (row['DiagnosticCode']).replace(';','_') if isinstance(row['DiagnosticCode'], str) else  ''
            #     if self.pauseBouncesCampaign is True:
            #         for elem in self.blocked_indication:
            #             if code.startswith(elem):
            #                 liste_campagne_to_stop.append(i)
            #     listeDiagnosticCode.append(code)
            #     listeFirstname.append('')
            #     listeLastname.append('')
            #     listeListes.append('')
            #     listFields.append('')
            #     listSuppressionLists.append('')
            #     listeMessageId.append(int(row['MessageId']))
            #     listeReason.append(row['Reason'])
            # if self.pauseBouncesCampaign is True:
            #     liste_campagne_to_stop = list(set(liste_campagne_to_stop))
            #     if len(liste_campagne_to_stop) > 0:
            #         for index in liste_campagne_to_stop:
            #             row_dict = df.loc[index].to_dict()
            #             self.stopSendouts(config=config, mydict=row_dict)
            # df_bounces = pd.DataFrame({
            #     "datetime": listeDate,
            #     "email": listeMd5,
            #     "reason" : listeReason,
            #     "sid" : listeMessageId,
            #     "tag" : listeTag,
            #     "diagnosticCode" : listeDiagnosticCode,
            #     "firstname" : listeFirstname,
            #     "lastname" : listeLastname,
            #     "domain" : listeDomain,
            #     "lists" : listeListes,
            #     "fields" : listFields,
            #     "supressionlists" : listSuppressionLists,
            #     # "advertiser": listeAdvertiser,
            #     # "agency": listeAgency
            # })
            # filename = str(int(config['dwh_id']))+'_Bounces_'+self.dateProcess+'.csv'
            # df_bounces.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            # os.remove(path_export_file)
        except Exception as e:
            print('error building bounces ',e)
            pass
        
    def build_complaints(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            df['sid'] = [ x for x in df['MessageId']]
            df['reason'] = [ '' for x in df['MessageId']]
            df['diagnosticCode'] = [ '' for x in df['MessageId']]
            df['firstname'] = [ '' for x in df['MessageId']]
            df['lastname'] = [ '' for x in df['MessageId']]
            df['lists'] = [ '' for x in df['MessageId']]
            df['supressionlists'] = [ '' for x in df['MessageId']]
            df['fields'] = [ '' for x in df['MessageId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            df['tag'] = [ self.processTag(config, int(x)) for x in df['MessageId']]
            columns = ['datetime','email','reason','sid','tag','diagnosticCode','firstname','lastname','domain','lists','fields','supressionlists']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Complaints_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)
        except Exception as e:
            print('error building complaints ',e)
            pass
    
    def build_opens(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            print(len(df))
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            df['sid'] = [ x for x in df['MessageId']]
            liste_sid = set(df['sid'])
            result = {}
            for sid in liste_sid:
                result[sid] = self.processTag(config, sid)
            df['reason'] = [ '' for x in df['MessageId']]
            df['diagnosticCode'] = [ '' for x in df['MessageId']]
            df['firstname'] = [ '' for x in df['MessageId']]
            df['lastname'] = [ '' for x in df['MessageId']]
            df['lists'] = [ '' for x in df['MessageId']]
            df['supressionlists'] = [ '' for x in df['MessageId']]
            df['fields'] = [ '' for x in df['MessageId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            df['tag'] = [ result[x] for x in df['MessageId']]
            columns = ['datetime','email','reason','sid','sid','diagnosticCode','firstname','lastname','domain','lists','fields','supressionlists']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Opens_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)
        except Exception as e:
            print('error building opens ',e)
            pass      
    
    def processTag(self, config, sid):
        try:
            additional_info = self.getCampaignInfoFromId(config, int(sid))
            return self.getTagsName(additional_info['tags_id']) if  additional_info['tags_id'] != '' else ''
        except Exception as e:
            return ''
    
    def build_sends(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            df['sid'] = [ x for x in df['MessageId']]
            liste_sid = set(df['sid'])
            result = {}
            for sid in liste_sid:
                result[sid] = self.processTag(config, sid)
            df['reason'] = [ '' for x in df['MessageId']]
            df['diagnosticCode'] = [ '' for x in df['MessageId']]
            df['firstname'] = [ '' for x in df['MessageId']]
            df['lastname'] = [ '' for x in df['MessageId']]
            df['lists'] = [ '' for x in df['MessageId']]
            df['supressionlists'] = [ '' for x in df['MessageId']]
            df['fields'] = [ '' for x in df['MessageId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            df['tag'] = [ result[x] for x in df['MessageId']]
            columns = ['datetime','email','reason','sid','tag','diagnosticCode','firstname','lastname','domain','lists','fields','supressionlists']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Sends_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)
        except Exception as e:
            print('error building sends ',e)
            pass 
        
    def build_subscriptions(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['datetime'] = [ x for x in df['Date']]
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['listid'] = [ x for x in df['ListId']]
            df['listname'] = [ x for x in df['ListId']]
            df['firstname'] = [ '' for x in df['ListId']]
            df['lastname'] = [ '' for x in df['ListId']]
            df['supressionlists'] = [ '' for x in df['ListId']]
            df['fields'] = [ '' for x in df['ListId']]
            df['domain'] = [ (x.split('@'))[1]  for x in df['Email']]
            columns = ['datetime','email','listid','listname', 'firstname', 'lastname', 'domain', 'lists', 'fields', 'supressionlists']
            
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Subscriptions_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)
        except Exception as e:
            print('error building Subscriptions  ',e)
            pass 
        
    def build_unsubscriptions(self, path_export_file, config):
        try:
            df = pd.read_csv(path_export_file, low_memory=False)
            df['email'] = [ hashlib.md5(x.encode()).hexdigest() for x in df['Email']]
            df['datetime'] = [ x for x in df['Date']]
            columns = ['datetime','email']
            df = df.reindex(columns=columns)
            colonnes_a_supprimer = [col for col in df.columns if col not in columns]
            df = df.drop(columns=colonnes_a_supprimer)
            filename = str(int(config['dwh_id']))+'_Unsubs_'+self.dateProcess+'.csv'
            df.to_csv(os.path.join(os.path.dirname(path_export_file), filename), index=False)
            os.remove(path_export_file)          
        except Exception as e:
            print('error building Unsubscriptions  ',e)
            pass 
     
    def zipper_directory(self,nom_dossier, nom_zip):
        with zipfile.ZipFile(nom_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for dossier_actuel, sous_dossiers, fichiers in os.walk(nom_dossier):
                for fichier in fichiers:
                    chemin_absolu = os.path.join(dossier_actuel, fichier)
                    chemin_rel = os.path.relpath(chemin_absolu, nom_dossier)
                    zipf.write(chemin_absolu, arcname=chemin_rel)
                    
    def zip_file(self,file_paths, zip_path):
        try:
            with zipfile.ZipFile(zip_path, "w") as zip:
                zip.write(file_paths,arcname=os.path.basename(file_paths))
        except Exception as e:
            print('error zip file ',e)
            pass
                       
    def make_activity_export(self,events, path, config_domain):
        try:
            api_url = f'''{config_domain["api_url"] + self.api_path_methods}?apikey={config_domain["api_key"]}'''
            api_events = api_url + '&type=' + events['events'] + '&date=' + self.dateProcess
            
            if events['events'] == 'Clicks':
                start = datetime.now()
                path_clicks = self.downloadFile(api_events,path)
                print(f' Clicks ------------------ {os.path.basename(path_clicks)}')
                self.build_clicks(path_clicks, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
            
            if events['events'] == 'Bounces':
                start = datetime.now()
                path_bounces = self.downloadFile(api_events,path)
                print(f' Bounces ------------------ {os.path.basename(path_bounces)}')
                self.build_bounces(path_bounces, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
            
            if events['events'] == 'Complaints':
                start = datetime.now()
                path_complaints = self.downloadFile(api_events,path)
                print(f' Complaints ------------------ {os.path.basename(path_complaints)}')
                self.build_complaints(path_complaints, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
                
            if events['events'] == 'Opens':
                start = datetime.now()
                path_opens = self.downloadFile(api_events,path)
                print(f' Opens ------------------ {os.path.basename(path_opens)}')
                self.build_opens(path_opens, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
                
            
            if events['events'] == 'Sends':
                start = datetime.now()
                path_sends = self.downloadFile(api_events,path)
                print(f' Sends ------------------ {os.path.basename(path_sends)}')
                self.build_sends(path_sends, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
                
            
            if events['events'] == 'Subscriptions':
                start = datetime.now()
                path_subscriptions = self.downloadFile(api_events,path)
                print(f' Subscriptions ------------------ {os.path.basename(path_subscriptions)}')
                self.build_subscriptions(path_subscriptions, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
                
            
            if events['events'] == 'Removals':
                start = datetime.now()
                path_removals = self.downloadFile(api_events,path)
                print(f' Removals ------------------ {os.path.basename(path_removals)}')
                self.build_unsubscriptions(path_removals, config_domain)
                print(f'{events["events"]} for {config_domain["acronyms"]} at {start} => {datetime.now() - start}' )
            
        except Exception as e:
            print('error exporting clicks ',e)
            pass
    
    def pauseNewsletters(self, config, sid):
        status = False
        try:
            # url = config['api_url']+self.api_path_pause + str(sid)
            # data = f'''
            #     <ApiRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema">
            #         <ApiKey>{(config['api_key']).strip()}</ApiKey>
            #         <Action>PauseMessage</Action>
            #     </ApiRequest>      
            # '''
            # r = requests.put(url, data=data)
            # if r.status_code == 200 or r.status_code == 201:
            #     status = True
            # return status
            time.sleep(2)
            return True
        except Exception as e:
            print('error pause newsletters ',e)
            return status
        
    def stopSendouts(self, config, mydict):
        try:
            status = self.pauseNewsletters(config,mydict['MessageId'])
            if status:
                #### write log ######
                directory_log = os.path.join(self.pathLogPaused, config['acronyms']+'_'+self.dateProcess)
                try:
                    os.mkdir(directory_log)
                except Exception as e:
                    pass
                filename = config['acronyms']+'_'+self.dateProcess+'_'+str(mydict['MessageId'])+'.txt'
                RED = "\033[31m"
                logs_paused = f'-{str(mydict["MessageId"])} on {mydict["domain"]} was paused due to this error message => {mydict["diagnosticCode"]} at {datetime.now()} \n'
                with open(os.path.join(directory_log,filename),'w') as fic:
                    fic.write(logs_paused)
                notif = Notification()
                # notif.send_notification_paused_campagn(emails=(config['notification']).split(','), database=config['basename'], sid=str(mydict['MessageId']), domain=mydict['domain'], errorcode=mydict["diagnosticCode"])
        except Exception as e:
            print('error stopping campagns ',e)
            pass
        
    def uploadToSftp(self, databaseFolder):
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            srv = pysftp.Connection(self.sftp['sftphost'], username=self.sftp['sftpuser'], password=self.sftp['sftppassword'], cnopts=cnopts)
            srv.cwd(self.sftp['sftppath'])
            srv.put(databaseFolder)
            srv.close()
            print('zip uploaded')
        except Exception as e:
            print('error uploading to sftp  ',e)
            pass
        
    def start_process_segments_all(self, config_file):
        start_date = datetime.now()
        logsFilename = os.path.join(self.pathLogSegment, self.dateProcess+".txt")  
        sys.stdout = open(logsFilename +'.txt','a')
        try:
            df = pd.read_excel(config_file)
            myconfig = []
            for i, rows in df.iterrows():
                if int(rows['segment']) == 1:
                    rows = self.setPreExport(rows)
                    if rows is not None:
                        data = rows.to_dict()
                        myconfig.append(data)
                    
                        
            print('pre-export done the config file')
            print('request for links download')
            ######################### Waiting for link ################################
            for newconfig in myconfig:
                newconfig = self.requestForDownloadLinks(newconfig)
            print('all requests sent for the config')
            print("Waiting for the process at ES")
            start = datetime.now()
            ##################### waiting for the links to be available ###############
            while any(d.get("download_links") == "Queued" or d.get("download_links") == "InProgress" for d in myconfig):
                in_queue = 0
                in_progress = 0
                finished = 0
                for newconfig in myconfig:
                    newconfig = self.requestForDownloadLinks(newconfig)
                    if newconfig["download_links"] == 'Completed':
                        finished += 1
                    if newconfig["download_links"] == 'InProgress':
                        in_progress += 1
                    if newconfig["download_links"] == 'Queued':
                        in_queue += 1 
                # time.sleep(self.waiting_delay)
                total_process = in_queue + in_progress + finished
                print('*' * 50)
                print(f'Total process => {total_process}')
                print(f'Completed  => {finished}')
                print(f'InProgress => {in_progress}')
                print(f'Queued     => {in_queue}')
                print('*' * 50)
                self.afficher_barre_progression(self.waiting_delay)
            ####################### download & extract segments #############################
            end = datetime.now()
            print(f'elapsed time for waiting all links to be download => {str(end - start)}')
            for newconfig in myconfig:
                filename = self.downloadAndExtract(newconfig) 
                self.zip_file(filename, filename.replace('.csv','.zip'))
                os.remove(filename)
            ####################### upload to sftp  #############################
            for sl in os.listdir(self.temp_sl):
                self.uploadToSftp(os.path.join(self.temp_sl, sl))
                # os.remove(os.path.join(self.temp_sl, sl))
            # for config in self.myconfig_sl:
            #     for files in os.listdir(self.temp_sl):
            #         self.buildSendableLists(config)
            #         print(f'done for {config["acronyms"]}') 
        except Exception as e:
            print('error at start process ',e)
            pass
        print('#' * 50)
        print(f"Process take {datetime.now() - start_date}")
        print('#' * 50)
        sys.stdout.close()
        sys.stdout = sys.__stdout__
          
    def setPreExport(self,config):
        try:
            print(f'prepare export for {config["acronyms"]}')
            config['id_exports'] = self.requestForSegmentToExport(config)
            return config
        except Exception as e:
            print('error on process sendable lists ',e)
            pass
        
    def getTimestampField(self,config):
        timestampfield = []
        try:
            urls = config['api_url']+'Api/Fields?apikey='+config['api_key']
            header = {'Content-Type': 'application/xml'}
            response = requests.get(urls,headers=header)
            xml_str = response.content
            xml_dict = xmltodict.parse(xml_str)
            if len(xml_dict['ApiResponse']['Data']['Fields']['Field']) > 0:
                for item in xml_dict['ApiResponse']['Data']['Fields']['Field']:
                    custom_fields = {"id": item['Id'], "name": item['Name']}
                    timestampfield.append(custom_fields)
            return   timestampfield      
        except Exception as e:
            print('error on process sendable lists ',e)
            return   timestampfield 
        
    def requestForSegmentToExport(self,config):
        try:
            timestamp_propriety = self.getTimestampField(config)
            if timestamp_propriety is not None:
                property = ''
                for item in timestamp_propriety:
                    property = property + f'<Property>{item["id"]}</Property>'
                payload_segmentt_export = f'''
                    <ApiRequest
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:xs="http://www.w3.org/2001/XMLSchema">
                        <ApiKey>{config["api_key"]}</ApiKey>
                        <Data>
                            <Type>Segment</Type>
                            <SegmentId>{str(int(config["segment_id_all"]))}</SegmentId>
                            <Fields>
                                <Field>Email</Field>
                                <Field>FirstName</Field>
                                <Field>LastName</Field>
                                <Field>CustomSubscriberId</Field>
                                <Field>IP</Field>
                                <Field>Vendor</Field>
                                <Field>TrackingCode</Field>
                                <Field>GeoCountry</Field>
                                <Field>GeoState</Field>
                                <Field>GeoCity</Field>
                                <Field>GeoZipCode</Field>
                                <Field>LastActivity</Field>
                                <Field>LastMessage</Field>
                                <Field>LastEmail</Field>
                                <Field>LastOpenEmail</Field>
                                <Field>LastClickEmail</Field>
                                <Field>SubscriptionDate</Field>
                            </Fields>
                            <Properties>
                                {property}
                            </Properties>
                        </Data>
                    </ApiRequest>
                '''
                header = {'Content-Type': 'application/xml'}
                url = config['api_url']+'Api/Exports'
                response = requests.post(url, data=payload_segmentt_export, headers=header)
                xml_str = response.content
                xml_dict = xmltodict.parse(xml_str)
                return xml_dict['ApiResponse']['Data']
        except Exception as e:
            print(f'error request for segment for {config["acronyms"]} => {e}')
            pass
        
    def requestForDownloadLinks(self,config):
        try:
            url = config['api_url']+'Api/Exports/'+str(config['id_exports'])+'?apikey='+str(config['api_key'])
            response = requests.get(url)
            xml_str = response.content
            xml_dict = xmltodict.parse(xml_str)
            config['download_links']= xml_dict["ApiResponse"]["Data"]["Status"]
            if xml_dict["ApiResponse"]["Data"]["Status"] == 'Completed':
                config['url_segments'] = xml_dict['ApiResponse']['Data']['DownloadUrl']
            return config
        except Exception as e:
            print('error requesting download links 1 => ',e)
            pass
        
    def downloadAndExtract(self,config):
        zipfileDownloaded = "sl.zip"
        filename = os.path.join(self.temp_sl, str(int(config['stats_id'])) +'_'+ str(int(config['segment_id_all'])) +'_all_'+ self.dateProcess +'.csv')
        try:
            print(f'url => {config["url_segments"]}')
            response = requests.get(config['url_segments'])
            with open(zipfileDownloaded, "wb") as f:
                f.write(response.content)
            with zipfile.ZipFile(zipfileDownloaded, "r") as zip_ref:
                csv_file_name = zip_ref.namelist()[0]
                zip_ref.extract(csv_file_name)
                os.rename(csv_file_name, filename)
            os.remove(zipfileDownloaded)
            # config['segment'] = filename
            return os.path.abspath(filename)
        except Exception as e:
            print('error downloading and extracting csv reports for openers ',e)
            pass
        
    def afficher_barre_progression(self,duree):
        widgets = [
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        ' (', progressbar.ETA(), ') ',
        ]

        barre = progressbar.ProgressBar(maxval=duree, widgets=widgets).start()

        for i in range(duree):
            time.sleep(1)  # Attendre 1 seconde
            barre.update(i + 1)

        barre.finish()