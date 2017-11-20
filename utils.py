import urllib2
import json
import base64
import logging
from config import *

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


def authenticated_http_req(url, user, pwd):
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (user, pwd)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    return request


def json_get_req(url):
    try:
        request = authenticated_http_req(url, ONOS_USER, ONOS_PASS)
        response = urllib2.urlopen(request)
        return json.loads(response.read())
    except IOError as e:
        logging.error(e)
        return ''


def json_post_req(url, json_data):
    try:
        request = authenticated_http_req(url, ONOS_USER, ONOS_PASS)
        request.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(request, data=json_data)
        return json.loads(response.read())
    except IOError as e:
        logging.error(e)
        return ''


def intent_stats():
    reply = json_get_req('http://%s:%d/onos/v1/imr/intentStats' % (ONOS_IP, ONOS_PORT))
    return reply['response'] if 'response' in reply else []


def avg(l):
    return 1.0*sum(l)/len(l)
