import requests

def authenticate(CLIENT_ID,SECRET_ID,PASSWORD,USERNAME):
    # Use HTTPBasicAuth to authenticate with Reddit
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_ID)

    data = {
        'grant_type': 'password',
        'username': USERNAME,
        'password': {PASSWORD}
    }
    
    headers = {
        'User-Agent': 'PoliticalLeanings/0.1'
        }
    
    response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    TOKEN = response.json()['access_token']

    headers['Authorization'] = f'bearer {TOKEN}'
    return headers

def get_top_comments(post_id, headers, limit):
    url = f'https://oauth.reddit.com/comments/{post_id}'
    params = {'limit': 30}  # Fetch more comments to ensure top ones are included
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch comments: {response.status_code}, {response.text}")

    data = response.json()

    # The second element of the returned list contains the comments
    comments = data[1]['data']['children']

    top_comments = []

    for comment in comments:
        if comment['kind'] == 't1':  # 't1' is the type for comment
            body = comment['data']['body']
            score = comment['data']['score']
            top_comments.append({'body': body, 'score': score})

    # Sort comments by score (karma)
    top_comments.sort(key=lambda x: x['score'], reverse=True)

    return top_comments[:limit]


def postTitlesID(response):
    post_id_list = []
    post_titles = []
    for post in response.json()['data']['children']:
        post_data = post['data']
        if post_data.get('stickied'):
            continue  # Skip stickied (pinned) posts
        post_id = post_data['id']
        post_id_list.append(post_id)
        post_titles.append(post_data['title'])
    return post_id_list, post_titles
