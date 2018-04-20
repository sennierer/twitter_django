from django.db import models
from .tasks import read_twitter
import tweepy
import time


def save_new_tweets(project_id, tweets):
    project = Project.objects.get(pk=project_id)


class Url(models.Model):
    url = models.URLField()
    shortened_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.url


class Hashtag(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class Account(models.Model):
    id = models.BigIntegerField(primary_key=True)
    handle = models.CharField(max_length=100)
    following = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.handle


class Message(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    by = models.ForeignKey(
        Account, on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name='authored_by')
    mentions = models.ManyToManyField(Account, blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    urls = models.ManyToManyField(Url, blank=True)
    text = models.TextField(blank=True, null=True)
    geo = models.CharField(max_length=50, blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.DO_NOTHING)
    deleted = models.BooleanField(default=False)
    retweeted = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name='retweeted_tweet')
    in_reply_to = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name='replied_tweet')
    reply_count = models.IntegerField(default=0)
    retweet_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)


class Project(models.Model):
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)
    account_timeline = models.BooleanField(default=True)
    follow_users = models.ManyToManyField(Account, blank=True)
    follow_terms = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="use comma to seperate the terms to filter on")
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    run = models.BooleanField(default=True)

    def create_tweet_from_id(self, tweet_id):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        res = api.get_status(tweet_id, tweet_mode='extended')._json
        m = self.add_new_tweets(res, drilldown=False)
        return m

    def add_new_tweets(self, tweet, drilldown=True):
        if 'extended_tweet' in tweet.keys():
            tweet['text'] = tweet['extended_tweet']['full_text']
        ts = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
        usr, created = Account.objects.get_or_create(
            id=tweet['user']['id'], handle=tweet['user']['screen_name']
        )
        m = Message.objects.create(
            id=tweet['id'],
            created_at=ts,
            text=tweet['text'],
            project=self,
            by=usr
        )
        mentions = []
        for usr in tweet['entities']['user_mentions']:
            query = Account.objects.filter(id=usr['id'])
            if query.count() == 0:
                u = Account.objects.create(id=usr['id'], handle=usr['screen_name'])
                mentions.append(u)
            elif query.count() == 1:
                mentions.append(query[0])
        for u in mentions:
            m.mentions.add(u)
        hashtags = []
        for tag in tweet['entities']['hashtags']:
            query = Hashtag.objects.filter(text=tag['text'])
            if query.count() == 0:
                t = Hashtag.objects.create(text=tag['text'])
                hashtags.append(t)
            elif query.count() == 1:
                hashtags.append(query[0])
        for t in hashtags:
            m.hashtags.add(t)
        if 'retweeted_status' in tweet.keys() and drilldown:
            m2 = self.add_new_tweets(tweet['retweeted_status'])
            m.retweeted = m2
            m.save()
        if tweet['in_reply_to_status_id'] is not None and drilldown:
            m3 = self.create_tweet_from_id(tweet['in_reply_to_status_id'])
            m.in_reply_to = m3
            m.save()
        return m

    def start(self, reset=False):
        r = read_twitter.delay(self.pk)
        self.celery_task_id = r.id
        self.save()
