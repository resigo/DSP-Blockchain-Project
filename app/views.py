import os
import datetime
import json
from markupsafe import Markup

import requests
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:" + str(os.environ.get('CONNECTED_NODE_PORT'))

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Linked Data Blockchain - ' + str(os.environ.get('APPLICATION_PORT')),
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/visual')
def visual():
    fetch_posts()
    return render_template('visual.html',
                           title='Linked Data Blockchain',
                           posts=posts)


def check_ids(d_or_l, keys_list, value_list):
    """
    Checking if all JSON-LD objects have unique ID
    """
    global count

    if isinstance(d_or_l, dict):
        count += 1
        for k, v in iter(sorted(d_or_l.items())):
            if isinstance(v, list) or isinstance(v, dict):
                check_ids(v, keys_list, value_list)

            elif k == "@id" or k == "id":
                keys_list.append(k)
                value_list.append(v)

    elif isinstance(d_or_l, list):
        for i in d_or_l:
            if isinstance(i, list) or isinstance(i, dict):
                check_ids(i, keys_list, value_list)

    if (len(value_list) == len(set(value_list))) and (count == len(keys_list)):
        return True

    else:
        return False


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    # WARNING: Insecure, all fields need to be checked: action type must be in "allowed list", etc.
    # Context
    action = request.form["action_type"].split("_")
    context = "request" if action[0] == "req" else "result"
    # Action
    action_type = action[-1]
    action_name = request.form["action_name"]
    action_desc = request.form["action_desc"]
    # Linked Data
    file = request.files["data"]
    if file:
        data = json.loads(file.read())

        # Init the UID checker
        keys_list = []
        value_list = []
        global count
        count = 0

        # Chech if every object has UID
        if not check_ids(data, keys_list, value_list):
            return "Some objects in the JSON-LD file are missing unique IDs. IDs found: " + ", ".join([i for i in value_list])

    else:
        return "No data were send to the Blockchain. Please, upload a file."

    # Agent: Person
    person_name = request.form["person_name"]
    person_org = request.form["person_org"]
    # Reference
    ref_tx = request.form["ref_transaction"]
    ref_object = request.form["ref_object"]

    post_object = {
        "@context": ["DSP/web-ledger", "DSP/" + context],
        "@id": None,
        "@type": "StorageBlock",
        "action": {
            "@type": action_type,
            "name": action_name,
            "description": action_desc,
            "agent": {
                "@type": "Person",
                "name": person_name,
                "organization": person_org,
            },
            "transaction_id": ref_tx,
            "object_id": ref_object,
        },
        "data": data
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    # return post_object  # Debug post object
    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%d. %m. %Y at %H:%M')


def to_pretty_json(value):
    return Markup(json.dumps(value, sort_keys=False,
                             indent=4, separators=(',', ': ')))


app.jinja_env.filters['tojson_pretty'] = to_pretty_json
