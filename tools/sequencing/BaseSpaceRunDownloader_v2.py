from urllib2 import Request, urlopen, URLError
from os.path import expanduser
import re
import hashlib
import json
import sys
import os
import json
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


CHUNK_SIZE = 128 * 1024
RunID = sys.argv[1]


with open('/galaxy/creds.json', 'r') as handle:
    data = json.load(handle)
    AccessToken = data['BaseSpace']

API_BASE = 'https://api.basespace.illumina.com/'
ACCESS_TOKEN = '?access_token=%s' % AccessToken


def restrequest(rawrequest):
    rawrequest = API_BASE + rawrequest + ACCESS_TOKEN
    log.debug('Req: ' + rawrequest.replace(AccessToken, '*' * len(AccessToken)))

    req_url_hash = hashlib.md5(rawrequest).hexdigest()
    cache_path_basedir = os.path.join(expanduser("~"), '.cache', 'basespace')
    if not os.path.exists(cache_path_basedir):
        os.makedirs(cache_path_basedir)

    cache_path = os.path.join(cache_path_basedir, req_url_hash)
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as handle:
            json_obj = json.load(handle)
            return json_obj

    log.debug("Cache miss")
    request = Request(rawrequest)

    try:
        response = urlopen(request)
        json_string = response.read()
        json_obj = json.loads(json_string)
    except URLError, e:
        print 'Got an error code:', e
        sys.exit()

    with open(cache_path, 'w') as handle:
        json.dump(json_obj, handle)

    return json_obj


json_obj = restrequest('v1pre3/runs/%s/samples' % RunID)

for sample in json_obj['Response']['Items']:
    sample_json_obj = restrequest(sample['Href'])

    files_obj = restrequest(sample_json_obj['Response']['HrefFiles'])

    for file in files_obj['Response']['Items']:
        potential_filename = file['Name']
        safe_filename = re.sub('[^A-Za-z0-9._-]', '', potential_filename)
        fastq_url = file['HrefContent']

        response = urlopen(API_BASE + fastq_url + ACCESS_TOKEN, timeout=10)

        content_length = int(response.info().getheader('Content-Length'))
        expected_chunks = content_length / CHUNK_SIZE

        if os.path.exists(safe_filename) and os.path.getsize(safe_filename) == content_length:
            log.info("%s already downloaded and is correct size" % safe_filename)
            continue
        elif os.path.exists(safe_filename):
            log.warning("%s exists but may be a partial download / different file" % safe_filename)
            sys.exit()

        with open(safe_filename, 'wb') as handle:
            i = 0
            while True:
                i += 1
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                handle.write(chunk)

print json.dumps(json_obj)
