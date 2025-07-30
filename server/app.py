#This python function will take in the posts from X, ask ChatGPT the political leaning of the post and output via JSON

from openai import OpenAI



def setupClient(API_KEY):
    global client
    if not API_KEY:
        raise ValueError("API key is required to initialize the OpenAI client.")
    client = OpenAI(api_key=API_KEY)
    return client


def get_political_leaning(post):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a political analyst. You only give political leanings of comments under online posts in one word answers. Your options are:  left, center, neutral, right"},
            {"role": "user", "content": f"Analyze the following post title and comment and determine the commentors political leaning with one word with all lower case: {post}"}
        ]
    )
    return response.choices[0].message.content

