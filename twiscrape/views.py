from django.shortcuts import render
from .filter import MessageFilter
from .forms import GenericFilterFormHelper
from .tables import MessagesTable
from django_tables2 import SingleTableView
from .models import Message
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class TweetsList(SingleTableView):
    formhelper_class = GenericFilterFormHelper
    context_filter_name = 'filter'
    paginate_by = 25
    template_name = 'twiscrape/messages_list.html'
    table_class = MessagesTable
    filterset_class = MessageFilter

    def get_queryset(self, **kwargs):
        self.project_id = self.kwargs.get('project_id')
        qs = Message.objects.filter(project_id=self.project_id)
        self.filter = MessageFilter(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(TweetsList, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context
