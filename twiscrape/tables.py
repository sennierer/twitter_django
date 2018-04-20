import django_tables2 as tables
from django_tables2.utils import A
from .models import Message


class MessagesTable(tables.Table):
    by = tables.LinkColumn('twiscrape:account-detail', args=[A('by_id')])
    #project = tables.LinkColumn('twiscrape:project-detail', args=[A('pk')])
    hashtags = tables.ManyToManyColumn()
    mentions = tables.ManyToManyColumn()


    class Meta:
        model = Message
        fields = ['text']
        # add class="paleblue" to <table> tag
        attrs = {"class": "table table-hover table-striped table-condensed"}


    def __init__(self, *args, exclude_columns=None, **kwargs):
        super().__init__(*args, **kwargs)
        if exclude_columns is not None:
            self.exclude = exclude_columns
