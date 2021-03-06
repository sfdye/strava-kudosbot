from __future__ import print_function

import logging
import os
import sys

import sendgrid
from flask import Flask, request
from sendgrid.helpers.mail import *
from stravalib import Client

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)


def send_email(athlete, activity):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("no-reply@stravakudosbot.com")
    subject = "Kudos on your {}!".format(activity.name)
    to_email = Email(athlete.email)
    content = Content("text/plain",
                      """
                      Hi {} {},
                      
                      Well done!
              
                      Keep up the good work,
                      
                      From the friendly Strava Kudos Bot🤖
                      """.format(athlete.firstname, athlete.lastname)
                      )
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logger.info(response.status_code)
    logger.info(response.body)
    logger.info(response.headers)


def give_kudos(activity_id):
    client = Client(access_token=os.environ.get('STRAVA_ACCESS_TOKEN'))
    activity = client.get_activity(activity_id)
    logger.info('activity = {}'.format(activity))
    athlete = client.get_athlete(activity.athlete.id)
    logger.info('Giving kudos to {}'.format(athlete.username))
    logger.info('Email: {}'.format(athlete.email))
    send_email(athlete, activity)


@app.route("/webhook", methods=['POST'])
def webhook():
    logger.info('payload = \n{}'.format(request.json))
    data = request.json
    activity_id = int(data['activity_link'].strip().split('/')[-1])
    give_kudos(activity_id)
    return 'ok'
