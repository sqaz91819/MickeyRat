from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Question, Choice, Query, ScoreMovie
import sys
sys.path.insert(0, 'D:\GitHub\MickeyRat')


from crawler_api import mongodb


class IndexView(generic.ListView):
    model = Query
    form_class = Query
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            with mongodb.Mongodb(hash_check=False) as mgd:
                temp = mgd.search_title('articles', form.query['search'])
                pos = [t['score'] for t in temp if t['score'] > 3]
                neg = [t['score'] for t in temp if t['score'] == 3]
                temp = [t['score'] for t in temp if t['score'] > 0]
                neutral = len(temp) - len(pos) - len(neg)

            # temp = [1, 2, 3, 4, 5, 1, 1, 4, 4, 4, 4]
            # pos = [t for t in temp if t > 3]
            # neg = [t for t in temp if t == 3]
            # temp = [t for t in temp if t > 0]
            # neutral = len(temp) - len(pos) - len(neg)
            try:
                score = (sum(temp) / len(temp)) * 21
                articles = len(temp)
            except ZeroDivisionError:
                return render(request, self.template_name, {
                    'form': form,
                    'error_message': '請輸入正確電影名稱，若沒輸入錯誤，就是該電影還未加入資料庫請見諒',
                })

            return render(request, self.template_name, {
                'form': form,
                'search_valid': True,
                'query': form.query['search'],
                'movie_score': int(score),
                'articles': articles,
                'pos': len(pos),
                'neg': len(neg),
                'neutral': neutral,
            })

        return render(request, self.template_name, {
            'form': form,
            'error_message': 'Please enter movie name',
        })


class DetailView(generic.ListView):
    model = Query
    template_name = 'polls/detail.html'


class ResultsView(generic.ListView):
    model = Query
    template_name = 'polls/results.html'


class LabelView(generic.ListView):
    model = Query
    template_name = 'polls/labelfix.html'


class ModifyView(generic.ListView):
    model = ScoreMovie
    form_class = ScoreMovie
    template_name = 'polls/modify.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            score = form.score['score2']
            movie = form.score['movie2']
            with mongodb.Mongodb() as mgd:
                article = mgd.search_dual('articles', 'title', movie, 'score', int(score))
            try:
                return render(request, self.template_name, article)
            except IndexError:
                return render(request, 'polls/labelfix.html', {'error_message': '資料庫無此電影或沒有該範圍分數的文章'})

        return render(request, 'polls/labelfix.html', {'error_message': 'Not valid input.'})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

