import os.path
import markovify
import urllib.request
import json
import sys
from nltk import tokenize

GROUPME_URL = 'https://api.groupme.com/v3'

if not os.path.isfile('.API_KEY'):
    print("You need write your access token to make API requests")
    access_token = input('> ')
    with open('.API_KEY', 'w') as f:
        f.write(access_token)
else:
    with open('.API_KEY', 'r') as f:
        access_token = f.read().rstrip()


def create_bot(name, avatar_url, group_id):
    params = urllib.parse.urlencode({
        'bot': {
            'group_id': group_id,
            'avatar_url': avatar_url,
            'name': name,
        }
    })
    request_url = urllib.request.Request(request_url, params.encode('ascii'))
    try:
        response = urllib.request.urlopen(request_url)
    except urllib.error.HTTPError as e:
        print(e)


def generate_user_model(message_list):
    data = filter(None, message_list)
    text_data = ''
    print(len(message_list))
    for message in data:
        tokenized_text = tokenize.sent_tokenize(message)
        text = '\n'.join(tokenized_text)
        text_data += text + '\n'
    model = markovify.NewlineText(text_data)
    return model


def write_user_model(name, model):
    user_name = name.lower().replace(' ', '_') + '.json'
    model_json = model.to_json()
    with open(user_name, 'w') as f:
        json.dump(model_json, f)


def read_user_model(user_name):
    with open(user_name, 'r') as f:
        model_json = json.load(f)
        model = markovify.NewlineText.from_json(
            model_json
        )
    return model


def get_user_model(user_name, message_list):
    if not os.path.isfile(user_name + '.json'):
        # print('No ' + user_name + '.json found.')
        # print('Generating model for ' + user_name)
        model = generate_user_model(message_list)
        write_user_model(user_name, model)
    else:
        # print('Reading ' + user_name + '.json from file.')
        read_user_model(user_name + '.json')


def generate_user_list(message_list):
    user_list = {}
    for message in message_list:
        name = message['name']
        user_id = message['user_id']
        avatar_url = message['avatar_url']
        user_message_list = [
            m['text'] for m in message_list if m['user_id'] == user_id
            and m['text'] is not None
        ]
        message_list[:] = [
            m for m in message_list
            if not m['user_id'] == user_id
        ]
        if not user_message_list == []:
            user_list[name] = {
                'message_list': user_message_list,
                'id': user_id,
                'avatar_url': avatar_url
            }
    return user_list


def get_user_list(message_list):
    if not os.path.isfile('user_list.json'):
        print('No user_list.json found.')
        print('Generating user_list.')
        user_list = generate_user_list(message_list)
        write_user_list(user_list)
    else:
        print('Reading user_list.json from file.')
        user_list = read_user_list()
    return user_list


def write_user_list(model):
    with open('user_list.json', 'w') as f:
        json.dump(model, f)


def read_user_list():
    with open('user_list.json', 'r') as f:
        model_list = json.load(f)
    return model_list


def get_message_list_url(group_id):
    messages_url = '/groups/' + group_id + '/messages'
    limit_url = '&limit=100'
    token_url = '?token=' + access_token
    message_list_url = GROUPME_URL + messages_url + token_url + limit_url
    return message_list_url


def format_message_list(message_list):
    message_list = filter(None, message_list)
    text_data = ''
    for message in message_list:
        tokenized_text = tokenize.sent_tokenize(message)
        text = '\n'.join(tokenized_text)
        text_data += text + '\n'
    return message_list


def generate_message_list(group_list):
    message_list = []
    for group in group_list:
        group_id = group['id']
        print(group_id)
        before_id = ''
        while True:
            message_list_url = get_message_list_url(group_id)
            message_list_url += '&before_id=' + before_id
            print(message_list_url)
            try:
                response = urllib.request.urlopen(message_list_url)
            except urllib.error.HTTPError as e:
                print(e)
                break
            response_json = json.loads(response.read().decode('utf-8'))
            message_list_json = response_json['response']['messages']
            if not message_list_json == []:
                message_list += message_list_json
                last_message = message_list_json[-1]
                before_id = last_message['id']
            else:
                break
    # message_list.insert(0, before_id)
    return message_list


def update_message_list(group_list):
    with open('message_list.json', 'r') as f:
        message_list = json.load(f)
        after_id = message_list[0]['id']
    for group in group_list:
        group_id = group['id']
        print(group_id)
        while True:
            message_list_url = get_message_list_url(group_id)
            message_list_url += '&after_id=' + after_id
            print(message_list_url)
            try:
                response = urllib.request.urlopen(message_list_url)
            except urllib.error.HTTPError as e:
                print(e)
                break
            response_json = json.loads(response.read().decode('utf-8'))
            message_list_json = response_json['response']['messages']
            if not message_list_json == []:
                message_list += message_list_json
                first_message = message_list_json[0]
                after_id = first_message['id']
            else:
                break
    # message_list.insert(0, before_id)
    return message_list


def write_message_list(message_list):
    with open('message_list.json', 'w') as f:
        json.dump(message_list, f)


def read_message_list():
    with open('message_list.json', 'r') as f:
        message_list = json.load(f)
    return message_list


def get_message_list(group_list):
    if not os.path.isfile('message_list.json'):
        print('No message_list.json found.')
        print('Generating message_list.')
        message_list = generate_message_list(group_list)
        write_message_list(message_list)
    else:
        print('Reading message_list.json from file.')
        message_list = update_message_list(group_list)
        write_message_list(message_list)
    return message_list


def get_group_list_request_url(page):
    groups_url = '/groups'
    token_url = '&token=' + access_token
    params = '?page=' + str(page) + '&per_page=100'
    group_list_request_url = GROUPME_URL + groups_url + params + token_url
    return group_list_request_url


def generate_group_list():
    group_list = []
    page = 1
    while True:
        try:
            request_url = get_group_list_request_url(page)
            response = urllib.request.urlopen(request_url)
        except urllib.error.HTTPError as e:
            print(e)
            sys.exit()
        group_list_json = json.loads(response.read().decode('utf-8'))
        page += 1
        if group_list_json['response']:
            group_list += group_list_json['response']
        else:
            break
    return group_list


def write_group_list(group_list):
    with open('group_list.json', 'w') as f:
        json.dump(group_list, f)


def read_group_list():
    with open('group_list.json', 'r') as f:
        group_list = json.load(f)
    return group_list


def get_group_list():
    if not os.path.isfile('group_list.json'):
        print('No group_list.json found.')
        print('Generating group_list.')
        group_list = generate_group_list()
        write_group_list(group_list)
    else:
        print('Reading group_list.json from file.')
        group_list = read_group_list()
    return group_list


# def combine_models():
#     model_list = []
#     for arg in argv[2:]:
#         with open(arg, 'r') as f:
#             model_json = json.load(f)
#             model = markovify.NewlineText.from_json(
#                 model_json
#             )
#             model_list.append(model)
#     markovify.combine(model_list)


def main():
    if len(sys.argv) == 1:
        group_list = get_group_list()
        message_list = get_message_list(group_list)
        print(len(message_list))
        user_list = get_user_list(message_list)
        for user in user_list:
            get_user_model(user, user_list[user]['message_list'])
    elif sys.argv[1] == 'combine' and len(sys.argv) > 2:
        model_list = []
        for arg in sys.argv[2:]:
            model = read_user_model(arg)
            model_list.append(model)
        model_combo = markovify.combine(model_list)
        name = sys.argv[2].split('.')[0]
        write_user_model(name, model_combo)
        for arg in sys.argv[3:]:
            os.remove(arg)
    else:
        for arg in sys.argv[1:]:
            model = read_user_model(arg)
            while True:
                text = model.make_sentence()
                if text is not None:
                    break
            print(text)


if __name__ == '__main__':
    main()
