import innertiktoken
from flask import Flask, request, jsonify, Response
import signal
import json
import socket
import textwrap
import os
import threading
import requests
import platform
import sys
sys.stdout = sys.stderr = open(os.devnull, 'w')

SHUTDOWN_FLAG = False
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/close', methods=['GET'])
def close():
    isWindows=platform.system()=="Windows"
    if isWindows:
        global SHUTDOWN_FLAG
        SHUTDOWN_FLAG = True
        return 'Server shutting down...'

@app.route('/')
def index():
    return 'site opened'


@app.after_request
def after_request(response: Response):
    global SHUTDOWN_FLAG
    if SHUTDOWN_FLAG:
        def shutdown():
            os.kill(os.getpid(), signal.SIGINT)

        # スレッドを作成してレスポンスが返された後にサーバーを停止する
        t = threading.Thread(target=shutdown)
        t.start()
    return response


def find_available_port(port):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return port
        except OSError:
            port += 1


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = innertiktoken.encoding_for_model(model)
        print("encoding", encoding)
    except KeyError:
        encoding = innertiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
        tokens_per_name = -1
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        print("message", message)
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


@app.route("/count-tokens", methods=['POST'])
def count_tokens():
    messages = request.json
    token_num = num_tokens_from_messages(messages)
    return token_num


@app.route("/fit-tokens", methods=['POST'])
def fit_tokens():
    data = json.loads(request.data)
    messages = data["messages"]
    print("messages", messages)
    token_num = num_tokens_from_messages(messages)
    while token_num > 4000*0.8:
        messages.pop(1)
        token_num = num_tokens_from_messages(messages)
    return jsonify(messages)

# @app.route("/fit-tokens", methods=['POST'])
# def fit_tokens():
#     data = json.loads(request.data)
#     messages = data["messages"]
#     print("messages", messages)
#     token_num = num_tokens_from_messages(messages)
#     while token_num > 4000*0.8:
#         messages.pop(1)
#         token_num = num_tokens_from_messages(messages)
#     return jsonify(messages)


def send_sstp(event: str, refs):
    text = textwrap.dedent(f"""\
    NOTIFY SSTP/1.0
    Charset: UTF-8
    Sender: tiktoken-saori
    Event: {event}
    """)
    for i, ref in enumerate(refs):
        text += f"Reference{i}: {ref}\n"
    
    headers = {'content-type': 'text/plain'}
    response = requests.post('http://localhost:9801/api/sstp/v1', headers=headers,data=text)
    print(response.text)



if __name__ == "__main__":
    # import fcntl

    # lock_file = open('tiktoken.lock', 'w')

    # try:
    #     fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # except IOError:
    #     print("Another instance is already running, exiting...")
    initial_port = 19801
    port = find_available_port(initial_port)
    send_sstp(event="OnPortSelected",refs=[port])
    app.config["PORT"]=port
    app.run(port=port)
    # sys.exit(0)
