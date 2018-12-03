import praw
import smtplib
import configparser as cp
from email.message import EmailMessage
from datetime import timezone, datetime

UTC = timezone.utc

def get_age(post):
    now = datetime.now(tz=UTC)
    post_time = datetime.fromtimestamp(post.created_utc, tz=UTC)
    return (now - post_time).seconds/60

def is_lonely(post):
    return not len(post.comments) and get_age(post) > 30

def make_links(posts):
    link = '<a href="{url}">{text}</a>'
    links = (link.format(url=post.url, text=post.title) for post in posts)
    return '<br>'.join(links)

def send_message(posts, server, user, password, to):
    msg = EmailMessage()
    msg['Subject'] = 'Lonely Posts'
    msg['From'] = f'{user}@{".".join(server.split(".")[-2:])}'
    msg['To'] = [to]
    msg.set_content(make_links(posts), subtype='html')
    with smtplib.SMTP_SSL(server) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)

def main():
    cfg = cp.ConfigParser()
    cfg.read('smtp.ini')
    reddit = praw.Reddit('lonely_posts')
    new_posts = reddit.subreddit('learnpython').new(params={'t':'day'})
    lonely_posts = [post for post in new_posts if is_lonely(post)]
    send_message(lonely_posts, **cfg['SMTP'])

if __name__ == '__main__':
    main()
