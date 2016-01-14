"""
Simplt Flask app that acts as a reasonably generic endpoint for
posting to Google pubsub.

Configuration is controlled by the "config" file
run from the same directory as the app.

"""

import hashlib
import json
import sys
import logging

from flask import Flask, abort, jsonify, request

from tools import generate_id, get_config_parser, get_pubsub_client, publish

app = Flask(__name__)

config = get_config_parser('config', app.logger)
app.logger.setLevel(config.get('override', 'log_level'))

format_str = '%(asctime)s\t%(levelname)s ' \
             '-- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
formatter = logging.Formatter(format_str)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(config.get('override', 'log_level'))

app.logger.addHandler(stdout_handler)

PROJ_NAME = config.get('override', 'proj_name')

pubsub_client = get_pubsub_client()



@app.route('/')
def index():
    """Generic just because"""
    return 'producer!'


@app.route(config.get('override', 'health_route'))
def ping():
    """health"""
    app.logger.info('health check')
    return 'pong'


@app.route(config.get('override', 'post_route'), methods=['POST'])
def producer():
    """Generic JSON POST"""

    reqdat_ = generate_id()

    app.logger.debug('webservice processing request')
    app.logger.debug(json.dumps(reqdat_))

    if not request.json:
        app.logger.debug('No json submitted')
        abort(400, 'Cannot interpret JSON post')

    try:
        hsh = json.dumps(request.json)
        resource_hash = hashlib.md5(hsh).hexdigest()
    except Exception as e:
        app.logger.debug('JSON is unhashable')
        abort(400, 'Cannot interpret JSON post')

    reqdat_['resource'] = request.json
    reqdat_['resource_hash'] = resource_hash

    try:
        app.logger.debug('writing to stream')
        publish(pubsub_client,
                config.get('override', 'stream_name'),
                json.dumps(reqdat_),
                app.logger,
                num_retries=config.getint('override', 'num_retries'))
    except Exception as e:
        app.logger.error(e)
        app.logger.error('failed to put to stream ' + json.dumps(reqdat_))
        abort(503, 'Internal Error')
        return json.dumps({'response': 'failure'})

    return json.dumps({'response': 'success'})


if __name__ == '__main__':

    app.run(debug=True, port=5001)
