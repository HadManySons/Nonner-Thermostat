import praw
import Nonner_Thermostat_config
import time
import os
import csv
import datetime
import random
import requests
import json


def logger(x):
    with open ('Nonner_Thermostat_running_info.txt','a') as f:
        f.write('Nonner Thermostat,' + x + ',')
        f.write (str(datetime.datetime.now()) + '\n')
    #print ("Nonner Thermostat " + x + " " + str(datetime.datetime.now()))

def bot_login(): #signs in to Reddit
    r = praw.Reddit(username = Nonner_Thermostat_config.username,
            password = Nonner_Thermostat_config.password,
            client_id = Nonner_Thermostat_config.client_id,
            client_secret = Nonner_Thermostat_config.client_secret,
            user_agent = "/u/Bahet")
    return r


def get_temp(): #gets the most 'current' temperature from a text file
    with open("Nonner_Thermostat_templist.txt", "r") as temp:
        templist = temp.read()
        #Python has sometimes been putting in a lot of decimal places
        #this shortens them before returning
        if templist[2] == '.':
            return float(templist[0:4])
        if templist[1] == '.':
            return float(templist[0:2])
        return float(templist)

def get_base(): #gets the bases and their zipcodes
    with open('base_names.csv', newline='') as csvfile:
            baselist = []
            ziplist = []
            base_names = csv.reader(csvfile, delimiter=',', quotechar='|')
            for name in base_names:
                baselist.append(name[0]) #list of bases
                ziplist.append(name[1]) #list of associated zip codes
            length = len(baselist)
            x = random.randint(1,length-1) #randomly selects base
            return baselist[x], ziplist[x]

def get_wx(zipcode):
    #gets the weather from Open Weather Map for the base
    r= requests.get('http://api.openweathermap.org/data/2.5/weather?zip=' + str(zipcode) +',us&units=imperial&APPID=d09d68180d854383348b432f4100a7b6').json()
    #was getting errors when trying to have the API only return the temp value, so I'm just using 2 lines of code for it
    j = (r['main']) 
    return (j['temp'])


def run_bot(r, comments_replied_to, temp):
    commentnumber = 50
    for comment in r.subreddit('airforce').comments(limit=commentnumber): #for loop to read through comments
        text = str(comment.body)
        text = str.upper(text) #makes the text all capitalized so it isn't a factor when searching through a string
        if 'NONNER' in text and comment.id not in comments_replied_to and not comment.author == r.user.me():
            base, zipcode = get_base()
            wx = get_wx(zipcode)
            #print (wx)
            mycomment = ("Every time you mention nonners, they turn down the air conditioning 0.1 degrees.  The temperature outside at " + str(base) + " is a rough " + str(wx) + " degrees while inside is a very pleasant " + str(temp) + " degrees!")
            #print (mycomment)
            comment.reply(mycomment)
            #next 3 lines update the list of comments replied to
            comments_replied_to.append(comment.id)
            with open ("Nonner_Thermostat_comments_replied_to.txt","a") as f:
                f.write(comment.id+"\n")
            temp = float(temp)
            temp = temp - .1 #lowers the temperature for the next round
            if len(str(temp)) > 4:
                temp = str(temp)
                temp = temp[0:4]
            with open("Nonner_Thermostat_templist.txt", "w") as newtemp: #puts the new temp in the txt file
                newtemp.write(str(temp))
            with open ("Nonner_Thermostat_reply_data.txt", "a") as f: 
                f.write (str(comment.author) + ',')
                f.write (str(comment.id) +',')
                f.write (str(base) + ',')
                f.write (str(wx) + ',')
                f.write (str(temp) + ',')
                f.write (str(datetime.datetime.now()) + '\n')

def get_saved_comments():
    with open("Nonner_Thermostat_comments_replied_to.txt", "r") as f:
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
    return comments_replied_to

def main():
    logger('Start')
    r = bot_login()
    temp = get_temp()
    comments_replied_to = get_saved_comments()
    run_bot(r, comments_replied_to, temp)
    logger('End')


#main()
while True:
    main()
#    time.sleep(300)
    
