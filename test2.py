
from process import main
from getRed import fetch_reddit_posts

main(fetch_reddit_posts( 
    sorting_method="top", 
    time_frame="day", 
    num_posts=1, 
    num_comments=1
), upload=False)
