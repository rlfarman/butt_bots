#!/usr/bin/env python3
import markovify
import urllib.request
import json
import sys
from nltk import tokenize
import random

api_key = None

try:
    f = open('.API_KEY', 'r')
    api_key = f.read().replace('\n', '')
except:
    pass

token_url = '?token=' + api_key

base_url = 'https://api.groupme.com/v3'

butt_groups = ['21302929', '28138212', '27498349', '23797196', '16697607']

bot_group = '31090230'

bot_url = '/bots/post'

group_url = '/groups'

user_names = [
    'Jessie Friedman',
    'Jessie Malone',
    'Emily Dorn',
    'Emily dorn',
    'Nick Horst',
    'Hunter Dunn',
    'Jake Barokas',
    'Steven Aslin',
    'Steven Aslan',
    'John Lyon',
    'Keith Nussbaum',
    'Liz Chenok',
    'Meredith Cranston',
    'Nikki Antenucci',
    'Richie Farman',
    'Travis Gallatin',
    'Sela Patterson'
]

name_to_user = {
    'steven': 'Steven Aslin',
    'jessie': 'Jessie Malone',
    'nikki': 'Nikki Antenucci',
    'keith': 'Keith Nussbaum',
    'travis': 'Travis Gallatin',
    'nick': 'Nick Horst',
    'emily': 'Emily Dorn',
    'hunter': 'Hunter Dunn',
    'john': 'John Lyon',
    'jake': 'Jake Barokas',
    'richie': 'Richie Farman',
    'sela': 'Sela Patterson',
    'liz': 'Liz Chenok',
    'meredith': 'Meredith Cranston'
}


users = [
    'Steven Aslin',
    'Jessie Malone',
    'Nikki Antenucci',
    'Keith Nussbaum',
    'Travis Gallatin',
    'Nick Horst',
    'Emily Dorn',
    'Hunter Dunn',
    'John Lyon',
    'Jake Barokas',
    'Richie Farman',
    'Sela Patterson',
    'Liz Chenok',
    'Meredith Cranston',
]

bot_ids = {
    'STEVEN_BOT': '6571a5d69c264c176bc90e8740',
    'MEREDITH_BOT': '6f7e3826b9bc878062c8d775ff',
    'JESSIE_BOT': 'aa9e9e7b1b9bd79b5b0d10bb39',
    'NICK_BOT': '43300fb9cfff10c912e70ce548',
    'RICHIE_BOT': '0be8d6b89dcf376fdee2805639',
    'EMILY_BOT': 'abff8ece3bf2fa4ef947841441',
    'KEITH_BOT': '680ee612cf98c08e383915494e',
    'JOHN_BOT': '510845bfb41d652e46e123a1d5',
    'HUNTER_BOT': '3923e85f2ec7c52c786c16f60e',
    'NIKKI_BOT': '8d76f0bee318db02589d0694cf',
    'TRAVIS_BOT': 'a1bc4de875d757f4277a3328ce',
    'JAKE_BOT': 'e9c687714bbf1712ccd441e03a',
    'LIZ_BOT': 'df045d29aa6e68bc6692bbfbdc',
    'SELA_BOT': '7387e2a5c1a8693ca8a13bfbcb'
}


def generate_message(model_dict):
    for name in model_dict:
        bot_name = name.split(' ')[0].upper() + '_BOT'
        bot_id = bot_ids[bot_name]
        model = model_dict[name]
        while True:
            text = model.make_sentence()
            if text is not None:
                break
        print(bot_id, text)
        response = input("Send? [y/n]:")
        if response == 'y':
            id_url = '?bot_id=' + bot_id
            name_url = '&text=' + text.replace(' ', '+') + '"'
            params = urllib.parse.urlencode({ 'bot_id': bot_id, 'text': text })
            request_url = base_url + bot_url
            req = urllib.request.Request(request_url, params.encode('ascii'))
            try:
                request = urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                print(e)
                continue


def generate_data(group_id):
    data = {}
    before_id_url = ''
    while True:
        messages_url = '/' + group_id + '/messages'
        limit_url = '&limit=100'
        request_url = base_url + group_url + messages_url + token_url + limit_url
        print(request_url)
        if before_id_url:
            request_url += before_id_url
        try:
            request = urllib.request.urlopen(request_url)
        except urllib.error.HTTPError:
            break
        request_data = json.loads(request.read().decode('utf-8'))
        group_data = request_data['response']
        for message in group_data['messages']:
            name = message['name']
            user_id = message['id']
            text = message['text']
            if name in user_names:
                if name == 'Steven Aslan':
                    name = 'Steven Aslin'
                elif name == 'Emily dorn':
                    name = 'Emily Dorn'
                elif name == 'Jessie Friedman':
                    name = 'Jessie Malone'
                if name not in ['GroupMe', 'GroupMe Calendar']:
                    if name in data:
                        data[name].append(text)
                    else:
                        data[name] = [text]
            before_id_url = '&before_id=' + message['id']
    return data


def generate_markov_model(messages):
    data = filter(None, messages)
    text_data = ''
    for message in data:
        tokenized_text = tokenize.sent_tokenize(message)
        text = '\n'.join(tokenized_text)
        text_data += text + '\n'
        model = markovify.NewlineText(text_data)
    print(text_data)
    return model


def write_markov_model(name, model):
    model_json = model.to_json()
    with open(name + '.json', 'w') as f:
        json.dump(model_json, f)


def read_markov_model(name):
    with open(name + '.json', 'r') as f:
        model_json = json.load(f)
        model = markovify.NewlineText.from_json(
            model_json
        )
    return model


def write_model(data):
    for name in data.keys():
        model = generate_markov_model(data[name])
        write_markov_model(name, model)


def read_model(users):
    model_dict = {}
    for name in users:
        model = read_markov_model(name)
        model_dict[name] = model
    return model_dict


def generate_groupme_dump(groups):
    data = {}
    for group_id in groups:
        new_data = generate_data(group_id)
        for name in new_data:
            if name in data:
                data[name] += new_data[name]
            else:
                data[name] = new_data[name]
    return data


def read_groupme_dump():
    with open('butt_dump.json', 'r') as f:
        data = json.load(f)
    return data


def write_groupme_dump(data):
    with open('butt_dump.json', 'w') as f:
        json.dump(data, f)


def write_groupme_users(data):
    with open('butts.txt', 'w') as f:
        for name in data.keys():
            f.write(name + '\n')


def read_groupme_users():
    with open('butts.txt', 'r') as f:
        users = f.read().splitlines()
    return users


def main():
    if api_key == None:
        sys.exit()
    if len(sys.argv) > 1:
        butts = []
        if sys.argv[1] == 'new':
            data = generate_groupme_dump(butt_groups)
            write_groupme_dump(data)
            write_groupme_users(data)
            write_model(data)
        if sys.argv[1] == 'all':
            butts = users
        elif sys.argv[1] == 'random':
            butts = [random.choice(users)]
        else:
            butts = []
            for arg in sys.argv[1:]:
                user = name_to_user[arg.lower()]
                if user not in users:
                    sys.exit()
                butts.append(user)
        model_dict = read_model(butts)
        generate_message(model_dict)


if __name__ == '__main__':
    main()
