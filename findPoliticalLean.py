from scraper.app import authenticate, get_top_comments, postTitlesID
from server.app import get_political_leaning, setupClient
import requests
from collections import Counter
from dotenv import load_dotenv
import os


def load_env():
    load_dotenv()
    global CLIENT_ID, SECRET_ID , PASSWORD, API_KEY, USERNAME
    PASSWORD = os.getenv('PASSWORD')
    CLIENT_ID = os.getenv('CLIENT_ID')
    SECRET_ID = os.getenv('SECRET_ID')
    API_KEY = os.getenv('API_KEY')
    USERNAME = os.getenv('USERNAME')
    
#Get subreddit from user input, defaulting to 'AskReddit' if not provided
def get_subreddit(postAmount):
    print(f"Welcome to the Political Leanings Analyzer! This tool will analyze the political leanings of posts in a subreddit based on the top {postAmount} posts comments of the past week.")
    subreddit = 'AskReddit' # Change this to the subreddit you want to analyze
    subreddit = input("Enter the subreddit you want to analyze: ")  # Allow user to input subreddit, defaulting to 'ufc'
    if not subreddit:
        subreddit ='AskReddit'
        print(f"Defaulting to r/{subreddit}")
    return subreddit

# This function fetches the top posts from the subreddit and returns the response
def gather_post_data(subreddit, headers, postAmount):
    response = requests.get(f'https://oauth.reddit.com/r/{subreddit}/top', headers=headers, params={'limit': postAmount, 't': 'week'}) # Limit is the amount of posts to fetch
    print(f"Fetching posts from r/{subreddit}...")

    while response.status_code != 200:
        print(f"Failed to fetch posts from {subreddit}:", response.status_code)
        subreddit = input("Enter the subreddit you want to analyze: ")
        response = requests.get(f'https://oauth.reddit.com/r/{subreddit}/top', headers=headers, params={'limit': postAmount, 't': 'week'}) # Limit is the amount of posts to fetch
    return response

# This script will authenticate with Reddit, fetch posts, and analyze their political leanings
def main():
    load_env() # Load environment variables
    if not CLIENT_ID or not SECRET_ID or not PASSWORD or not API_KEY or not USERNAME:
        print("Please set CLIENT_ID, SECRET_ID, PASSWORD, Username and API_KEY in the .env file.")
        return
    headers = authenticate(CLIENT_ID, SECRET_ID, PASSWORD, USERNAME)
    setupClient(API_KEY) # Initialize OpenAI client with API key

    postAmount = 15 # Change this to the amount of posts you want to analyze
    commentAmount = 15 # Change this to the amount of comments you want to analyze per post

    subreddit = get_subreddit(postAmount)  # Get subreddit from user input

    response = gather_post_data(subreddit, headers, postAmount)  # Fetch posts from the subreddit
    
    post_id_list=[]
    post_titles = []
    # Extract post IDs and titles
    post_id_list, post_titles = postTitlesID(response)
    
    if not post_id_list:
        print("No posts found in the subreddit.")
        return
    
    post_leanings_titles = {}
    for index,post_id in enumerate(post_id_list):
        comments = get_top_comments(post_id, headers, limit=commentAmount)  # Limit is the amount of comments to fetch per post
        post_leanings = []
        for comment in comments:
            titleandbody = "Title: " + post_titles[index] + " Comment: "+ comment['body']
            # Get political leaning of the comment body
            political_leaning = get_political_leaning(titleandbody)
            post_leanings.append(political_leaning)

        # Count the occurrences of each political leaning
        if post_leanings:
            leaning_counts = Counter(post_leanings)
            most_common_leaning = leaning_counts.most_common(1)[0]
            post_leanings_titles[post_titles[index]] = most_common_leaning
        else:
            print(f"Skipping post '{post_titles[index]}' — no valid political leanings found.")


    subreddit_leanings = []
    for title, (leaning, count) in post_leanings_titles.items():
        subreddit_leanings.append(leaning)

    # Count the overall political leanings in the subreddit
    overall_counts = Counter(subreddit_leanings)
    print(f"\nOverall Political Leanings in the Subreddit {subreddit}:")
    for leaning, count in overall_counts.items():
        print(f"{leaning}: {count} posts")


if __name__ == '__main__':
    main()