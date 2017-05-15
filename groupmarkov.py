import os.path
import markovify
import urllib.request

if not os.path.isfile('.API_KEY'):
    print("You need write your access token to make API requests")
    access_token = input('> ')
    with open('.API_KEY', 'w') as f:
        f.write(access_token)
else:
    with open('.API_KEY', 'r') as f:
        access_token = f.read().rstrip()


def get_group_list_request_url(page):
    base_url = 'https://api.groupme.com/v3'
    groups_url = '/groups'
    token_url = '&token=' + access_token
    params = '?page=' + str(page) + '&per_page=1'
    request_url = base_url + groups_url + params +  token_url
    return request_url


def get_group_list():
    group_list = []
    page = 1
    while True:
        try:
            request_url = get_group_list_request_url(page)
            print(request_url)
            reponse = urllib.request.urlopen(request_url)
            print(response)
        except urllib.error.HTTPError as e:
            print(e)
            break
        group_list_json = json.loads(request.read().decode('utf-8'))
        group_list += group_list_json
        page += 1

    return group_list

def get_messages(group):

    return messages


def get_members(group):
    members = group.members()
    return members


def get_messages(group):
    messages = group.messages()
    while messages.iolder():
        pass
    return messages

def combine_models():
    model_list = []
    for arg in argv[2:]:
        with open(arg, 'r') as f:
            model_json = json.load(f)
            model = markovify.NewlineText.from_json(
                model_json
            )
            model_list.append(model)
    markovify.combine(model_list)


def main():
    print(access_token)
    group_list = get_group_list()
    print(group_list)
    for group in group_list:
        print(get_messages(group))
        print(get_members(group))
        print(get_messages(group))

if __name__ == '__main__':
    main()
