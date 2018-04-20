from django.shortcuts import render
from django.views.generic.detail import DetailView
from .filter import MessageFilter
from .forms import GenericFilterFormHelper
from .tables import MessagesTable
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
from .models import Message, Account
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


@method_decorator(login_required, name='dispatch')
class AccountDetail(DetailView):
    template_name = 'twiscrape/account_detail.html'
    model = Account

    def get_context_data(self, **kwargs):
        context = super(AccountDetail, self).get_context_data()
        table = MessagesTable(Message.objects.filter(by_id=self.kwargs.get('pk')))
        RequestConfig(self.request).configure(table)
        context['messages_table'] = table
        return context
