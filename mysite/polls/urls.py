from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^detail/$', views.DetailView.as_view(), name='detail'),
    url(r'^results/$', views.ResultsView.as_view(), name='results'),
    url(r'^label/$', views.LabelView.as_view(), name='label'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]

