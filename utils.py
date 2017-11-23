import base64
import json
import logging
import urllib2
from config import *

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


def authenticated_http_req(url, user, pwd):
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (user, pwd)).replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % base64string)
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


def bps_to_human_string(value, to_byte_per_second=False):
    if to_byte_per_second:
        value = value/8.0
        suffix = 'B/s'
    else:
        suffix = 'bps'

    for unit in ['', 'K', 'M', 'G']:
        if abs(value) < 1000.0:
            return '%3.1f %s%s' % (value, unit, suffix)
        value /= 1000.0
    return '%.1f %s%s' % (value, 'T', suffix)
