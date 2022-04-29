# /usr/bin/env python

import http.client
import uuid
import json
import configparser
import os

JSON_PRE_PAYLOAD = "[\r\t\t{\r\t\t\t\"Text\": \""
JSON_POST_PAYLOAD = "\"\r\t\t}\r]"

api_settings: configparser.SectionProxy


def load_config():
    global api_settings

    my_config = configparser.ConfigParser()
    config_dir = os.path.dirname(os.path.abspath(__file__))
    my_config.read(config_dir + '/app_settings.ini')

    print(my_config.sections())
    api_settings = my_config['API']


def get_payload(text_to_translate):
    global JSON_PRE_PAYLOAD, JSON_POST_PAYLOAD

    ret = JSON_PRE_PAYLOAD + text_to_translate + JSON_POST_PAYLOAD
    print("Payload: " + ret)

    return ret


def get_url(src_lang, dest_lang):
    ret = '/translate?to%5B0%5D=fil&api-version=3.0&from=en&profanityAction=NoAction&textType=plain'\
          + '&from=' + src_lang + '&to=' + dest_lang
    print("Request URL: " + ret)
    return ret


# Need GUID to keep from getting blocked by API
def get_guid():
    my_guid = str(uuid.uuid4())
    print("New GUID is: " + my_guid)
    return my_guid


# input is a string in JSON format
def parse_response(jsonResponse):
    doc = json.loads(jsonResponse)
    ret = doc[0]["translations"][0]["text"]

    print("The JSON Response Text Field: " + ret)

    return ret


def get_translation(textToTranslate, srcLang, destLang):
    load_config()

    conn = http.client.HTTPSConnection(api_settings['api-host'])

    headers = {
        'content-type': api_settings['content-type'],
        'X-RapidAPI-Host': api_settings['x-rapidapi-host'],
        'X-RapidAPI-Key': api_settings['x-rapidapi-key']
    }

    conn.request(api_settings['submit-type'], get_url(srcLang, destLang), get_payload(textToTranslate), headers)

    res = conn.getresponse()
    data = res.read()

    ret = data.decode("utf-8")
    print(ret)
    return parse_response(ret)


print(__name__)

if '__main__' == __name__:
    myTest = get_translation("I like to drink coffee!", "en", "fil")
    print("Test results of submitting 'I like to drink coffee': " + myTest)
