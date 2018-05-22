"""
TrackParcel Mycroft Skill.
"""
import sys
import requests
import json
import aftership
from os.path import dirname, abspath
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.skills.context import *

__author__ = 'aix'

LOGGER = getLogger(__name__)

class TrackParcelSkill(MycroftSkill):
    """
    TrackParcel Skill Class.
    """    
    def __init__(self):
        """
        Initialization.
        """
        super(TrackParcelSkill, self).__init__(name="TrackParcelSkill")
        self.couriers_index = dirname(__file__) + '/couriers.json'

    @intent_handler(IntentBuilder("TrackParcelRequestInitIntent")
                    .require("TrackParcelKeyword").build())
    @adds_context('TrackContext')
    def handle_tracking_init_intent(self, message):
        """
        Init Tracking Request
        """
        self.speak('What Courier Service Would You Like To Track ?', expect_response=True)
    
    @intent_handler(IntentBuilder("TrackParcelCourierInfoIntent").require("TrackParcelCourierKeyword").require("TrackContext").build())
    @adds_context('CourierContext')
    def handle_tracking_courierinfo_intent(self, message):
        """
        Get Courier Info
        """
        utterance = message.data.get('utterance').lower()
        
        def findSlug(keywords):
            keyword = keywords.lower()
            with open(self.couriers_index) as json_data:
                d = json.load(json_data)
                for keys, value in d:
                    self.speak("a");
                    if keyword in value:
                        self.speak(key)
                        return key
                    else:
                        return keyword
                    
        serviceSlug = findSlug(utterance)
        global courierService
        courierService = serviceSlug
        self.speak('Please Speak Your Tracking Number After This Message', expect_response=True)
    
    @intent_handler(IntentBuilder("TrackParcelResultIntent").require("TrackParcelNumberKeyword").require("CourierContext").build())
    def handle_tracking_result_intent(self, message):
        """
        Find Package Details
        """
        utterance = message.data.get('utterance').lower()
        trackingNumber = utterance
        api = aftership.APIv4('eae7efb7-6ac4-4b89-aeec-e620294cad33')
        
        def addTrackingDetails(courierService, trackingNumber):
            self.speak("Searching for your package, Please wait")
            resultdetail = api.trackings.post(tracking=dict(slug=courierService, tracking_number=trackingNumber, title="Title"))
            filterTrackingDetails(resultdetail, courierService, trackingNumber)
        
        def filterTrackingDetails(cobject, courierService, trackingNumber):
            tID = cobject["tracking"]["id"]
            tNumber = cobject["tracking"]["tracking_number"]
            tCdate =  cobject["tracking"]["created_at"]
            tUdate =  cobject["tracking"]["updated_at"]
            tSlug = cobject["tracking"]["slug"]
            tOrigin =  cobject["tracking"]["origin_country_iso3"]
            tDest =  cobject["tracking"]["destination_country_iso3"]
            tTag = cobject["tracking"]["tag"]
            resultMsg = "Your package with tracking number {0} created on date {1} updated on {2} with delivery service {3} from country of origin {4} to destination country {5} is currently {6}".format(tNumber, tCdate, tUdate, tSlug, tOrigin, tDest, tTag)
            self.speak(resultMsg)
            self.enclosure.ws.emit(Message("trackingObject", {'desktop': {'data': cobject}}))
            removeTrackingDetails(courierService, trackingNumber)

        def removeTrackingDetails(courierService, trackingNumber):
            r = api.trackings.delete(courierService, trackingNumber)

        addTrackingDetails(courierService, trackingNumber)

    def stop(self):
        """
        Mycroft Stop Function
        """
        pass


def create_skill():
    """
    Mycroft Create Skill Function
    """
    return TrackParcelSkill()
