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
from mycroft.messagebus.message import Message
from mycroft.skills.context import *
from word2number import w2n

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
    def handle_tracking_courierinfo_intent(self, message):
        """
        Get Courier Info
        """
        global courierService
        global courierLists
        global listofcouriers
        utterance = message.data.get('utterance').lower()
        with open(self.couriers_index) as json_data:
                courierLists = json.load(json_data)
        
        
        def findSlug(keywords):
            keyword = keywords.lower()
            listofcouriers = []
            for key, value in courierLists.items():
                if value.find(keyword) != -1:
                    listofcouriers.append(value)
            return listofcouriers
        
        listofcouriers = findSlug(utterance)
        if len(listofcouriers) > 1:
            for idx, courier in enumerate(listofcouriers):
                self.speak(str(idx + 1) + ' ' + courier)
            self.speak('Please choose a number', expect_response=True)
            self.set_context('SelectContext')
            
        elif len(listofcouriers) == 1:
            for key,value in courierLists.items():
                if(listofcouriers[0] == value):
                    LOGGER.info(listofcouriers[0])
                    courierService = listofcouriers[0]
            self.speak('Please Speak Your Tracking Number After This Message', expect_response=True)
            self.set_context('CourierContext')
        else:
            self.speak('Sorry no courier found')

    @intent_handler(IntentBuilder("TrackParcelMultipleSelectionIntent").require("TrackParcelSelectionNumber").require("SelectContext").build())
    @adds_context("CourierContext")
    def handle_tracking_multiple_selection(self, message):
        utterance = message.data.get('TrackParcelSelectionNumber').lower()
        selectNumber = w2n.word_to_num(utterance)
        if(len(listofcouriers[selectNumber - 1]) > 1):
            for key,value in courierLists.items():
                if listofcouriers[selectNumber - 1] == value :
                    courserService = key
            self.speak('Please Speak Your Tracking Number After This Message', expect_response=True)
            self.set_context("CourierContext")
        else: 
            self.speak('Sorry your selected number was not found')
        
        
    @intent_handler(IntentBuilder("TrackParcelResultIntent").require("TrackParcelNumberKeyword").require("CourierContext").build())
    def handle_tracking_result_intent(self, message):
        """
        Find Package Details
        """                
        def extractNum(splitUtterance):
            for word in splitUtterance:
                try:
                    extractedNumber = w2n.word_to_num(word)
                    return extractedNumber
                
                except:
                    isWord = word
                    self.speak("error here")
                    
        def addTrackingDetails(courierService, trackingNumber):
            self.speak("Searching for your package, Please wait")
            resultdetail = api.trackings.post(tracking=dict(slug=courierService, tracking_number=trackingNumber, title="Title"))
            filterTrackingCreateDetail(resultdetail, courierService, trackingNumber)
            
        def getTrackingDetails(courierService, trackingNumber):
            trackedParcelDetails = api.trackings.get(courierService, trackingNumber)
            self.enclosure.ws.emit(Message("trackingObject", {'desktop': {'data': str(trackedParcelDetails)}}))
            filterTrackedDetail(trackedParcelDetails, courierService, trackingNumber)
            
        def filterTrackingCreateDetail(cobject, courierService, trackingNumber):
            tcID = cobject["tracking"]["id"]
            tcNumber = cobject["tracking"]["tracking_number"]
            tcCdate =  cobject["tracking"]["created_at"]
            tcUdate =  cobject["tracking"]["updated_at"]
            tcSlug = cobject["tracking"]["slug"]
            tcOrigin =  cobject["tracking"]["origin_country_iso3"]
            tcDest =  cobject["tracking"]["destination_country_iso3"]
            tcTag = cobject["tracking"]["tag"]
            resultMsg = "Your package with tracking number {0} created on date {1} updated on {2} with delivery service {3} from country of origin {4} to destination country {5} is currently {6}".format(tcNumber, tcCdate, tcUdate, tcSlug, tcOrigin, tcDest, tcTag)
            self.speak(resultMsg)
            getTrackingDetails(courierService, trackingNumber)
        
        def filterTrackedDetail(cobject, courierService, trackingNumber):
            LOGGER.info(cobject)
            removeTrackingDetails(courierService, trackingNumber)
                
        def removeTrackingDetails(courierService, trackingNumber):
            r = api.trackings.delete(courierService, trackingNumber)

        utterance = message.data.get('utterance').lower()
        utter = utterance.replace("-", "")
        splitUtterance = utter.split()
        convertedList = []
        for idx, word in enumerate(splitUtterance):
            try:
                convertedList.append(str(w2n.word_to_num(word)))
            except:
                convertedList.append(word)

        LOGGER.info(convertedList)
        trackingNumber = ''.join(convertedList)
        api = aftership.APIv4('eae7efb7-6ac4-4b89-aeec-e620294cad33')

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
