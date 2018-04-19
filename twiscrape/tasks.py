from celery import shared_task, current_task
from django.contrib.contenttypes.models import ContentType
from celery.signals import task_postrun
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json


logger = get_task_logger(__name__)


class TweetDjListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        print(data)
        #data_ret.append(json.loads(data))
        data = json.loads(data)
        if 'id' in data.keys():
            tw = self.dj_project.add_new_tweets(data)
        elif 'deleted' in data.keys():
            message = ContentType.objects.get(
                app_label="twiscrape", model="message").model_class()
            m = message.objects.filter(pk=data['deleted']['id'])
            if m.count() == 1:
                m[0].deleted = True
                m.save()
        self.tweets_count += 1
        return self.tweets_count

    def on_error(self, status):
        print(status)

    def __init__(self, project, *args, **kwargs):
        self.dj_project = project
        self.tweets_count = 0
        super().__init__(*args, **kwargs)


@shared_task(soft_time_limit=90, time_limit=200)
def read_twitter(project_id):
    try:
        project = ContentType.objects.get(
            app_label="twiscrape", model="project").model_class()
        project = project.objects.get(pk=project_id)
        l = TweetDjListener(project)
        auth = OAuthHandler(
            project.consumer_key, project.consumer_secret)
        auth.set_access_token(
            project.access_token, project.access_token_secret)
        logger.info('starting stream')
        stream = Stream(auth, l)
        #stream.filter(follow=["20428671"])
        stream.userstream(encoding='utf8')
    except SoftTimeLimitExceeded:
        logger.info('ended the task')
        return 'ended the task'


@task_postrun.connect()
def check_if_restart(sender=None, headers=None, body=None, **kwargs):
    logger.info('got end signal from task {}'.format(sender.request.id))
    project = ContentType.objects.get(
        app_label="twiscrape", model="project").model_class()
    project = project.objects.get(celery_task_id=sender.request.id)
    if project.run:
        project.start(reset=False)
