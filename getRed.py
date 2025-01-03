import requests

# Fetch Reddit posts with sorting and timeframe options
def fetch_reddit_posts(subreddit="askreddit", sorting_method='top', time_frame='day', num_posts=1, num_comments=3, allow_nsfw=False):
    """
    Fetches posts from a subreddit with sorting and timeframe options, filtering NSFW if specified.
    
    :param subreddit: The subreddit to fetch posts from (e.g., 'AskReddit').
    :param sorting_method: The sorting method for the posts ('top', 'new', 'hot', 'rising', etc.).
    :param time_frame: The time frame for the sorting ('day', 'week', 'month', 'year', 'all').
    :param num_posts: The number of posts to retrieve.
    :param num_comments: The number of top comments to retrieve for each post.
    :param allow_nsfw: Whether to include NSFW posts.
    
    :return: A list of dictionaries, each containing 'title', 'body', 'comments', 'post_id', 'nsfw',
             'subreddit', and 'username'.
    """
    # Base Reddit URL
    base_url = f"https://www.reddit.com/r/{subreddit}/{sorting_method}.json?t={time_frame}&limit={num_posts * 3}"
    
    # Headers to mimic a browser request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    # Make the request to Reddit
    response = requests.get(base_url, headers=headers)
    
    # Ensure the response is successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from Reddit. Status code: {response.status_code}")
    
    # Get the posts data
    posts = response.json().get('data', {}).get('children', [])
    if not posts:
        raise Exception("No posts found in the subreddit.")
    
    # Initialize a list to hold the post data
    post_data = []
    
    # Filter and process posts
    for post in posts:
        try:
            post_info = post['data']
            nsfw = post_info.get('over_18', False)
            
            # Skip NSFW posts if not allowed
            if not allow_nsfw and nsfw:
                continue
            
            post_id = post_info['id']
            title = post_info['title']
            body = post_info.get('selftext', '')  # Default to empty string if missing
            username = post_info['author']
            subreddit_name = post_info['subreddit']
            
            # Fetch top comments for the post
            comments = fetch_top_comments(post_id, num_comments)
            
            # Add the post data to the list
            post_data.append({
                'title': title,
                'body': body,
                'comments': comments,
                'post_id': post_id,
                'nsfw': nsfw,
                'username': username,
                'subreddit': subreddit_name
            })
            
            # Stop once the desired number of posts is collected
            if len(post_data) >= num_posts:
                break
        except Exception as e:
            print(f"Error processing post: {e}")
            continue
    
    if len(post_data) < num_posts:
        print(f"Only {len(post_data)} posts available that match the criteria.")
    
    return post_data

# Fetch top comments for a given post ID
def fetch_top_comments(post_id, num_comments):
    """
    Fetches the top comments for a Reddit post.
    
    :param post_id: The post ID to fetch comments for.
    :param num_comments: The number of top comments to retrieve.
    
    :return: A list of top comments.    
    """
    # Construct the URL to fetch the comments
    url = f"https://www.reddit.com/comments/{post_id}.json"
    
    try:
        # Make the request to fetch the comments
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch comments. Status code: {response.status_code}")
        
        # Get the comments data
        comments = response.json()[1].get('data', {}).get('children', [])
        if not comments:
            print(f"No comments found for post {post_id}.")
            return []
        
        # Extract the top comments, ensuring validity
        top_comments = [
            comment['data'].get('body', '') for comment in comments[:num_comments]
            if 'data' in comment and 'body' in comment['data']
        ]
        return top_comments
    except Exception as e:
        print(f"Error fetching comments for post {post_id}: {e}")
        return []
