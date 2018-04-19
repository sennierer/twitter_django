import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(lookup_expr='contains',
                                     label='Text')
    hashtags = django_filters.CharFilter(
        name='hashtags__text', lookup_expr='contains',
        label='Hashtags')
    mentions = django_filters.CharFilter(
        name='mentions__handle', lookup_expr='contains',
        label='Mentions')

    class Meta:
        model = Message
        fields = ['text', 'hashtags', 'mentions']
