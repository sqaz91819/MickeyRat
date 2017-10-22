from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Question, Choice, Query, ScoreMovie, Score
import sys
from django.conf import settings
from copy import copy
from keras.preprocessing import sequence
sys.path.insert(0, 'D:\GitHub\MickeyRat')
from crawler_api import mongodb

fasttext_model = settings.FAST


class IndexView(generic.ListView):
    fasttext = copy(fasttext_model)
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
                # ! unhashable type ! nlp = mgd.search_title('jie_ba_Articles', form.query['search'])
                pos_articles = [t for t in temp if t['score'] > 3]
                pos = [t['score'] for t in temp if t['score'] > 3]
                neg = [t['score'] for t in temp if t['score'] == 3]
                temp = [t['score'] for t in temp if t['score'] > 0]
                neutral = len(temp) - len(pos) - len(neg)

            if len(pos_articles) > 0:
                about = True
            else:
                about = False

            # temp = [1, 2, 3, 4, 5, 1, 1, 4, 4, 4, 4]
            # pos = [t for t in temp if t > 3]
            # neg = [t for t in temp if t == 3]
            # temp = [t for t in temp if t > 0]
            # neutral = len(temp) - len(pos) - len(neg)
            try:
                score = (sum(temp) / len(temp)) * 21
                articles = len(temp)
                # ! unhashable type ! nlp = sequence.pad_sequences(nlp, maxlen=400)
                # ! unhashable type ! fasttext_score = int(sum(self.fasttext.predict(nlp, batch_size=32)) / len(temp) * 100)
            except ZeroDivisionError:
                return render(request, self.template_name, {
                    'form': form,
                    'error_message': '請輸入正確電影名稱，若沒輸入錯誤，就是該電影還未加入資料庫請見諒',
                })

            return render(request, self.template_name, {
                'form': form,
                'search_valid': True,
                'about': about,
                'query': form.query['search'],
                'movie_score': int(score),
                'articles': articles,
                'pos': len(pos),
                'neg': len(neg),
                'neutral': neutral,
                'pos_url0': pos_articles[0]['url'],
                'pos_title0': pos_articles[0]['title'],
                # ! unhashable type ! 'fast_text': fasttext_score,
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
                article: dict = mgd.search_dual('articles', 'title', movie, 'score', int(score))
            try:
                article['content'] = article['content'].replace(' ', '\n')
                article['id0'] = article['_id']
                return render(request, self.template_name, article)
            except IndexError:
                return render(request, 'polls/labelfix.html', {'error_message': '資料庫無此電影或沒有該範圍分數的文章'})
            except TypeError:
                return render(request, 'polls/labelfix.html', {'error_message': '資料庫無此電影或沒有該範圍分數的文章'})

        return render(request, 'polls/labelfix.html', {'error_message': 'Not valid input.'})


def score(request):
    if request.method == 'POST':
        form = Score(request.POST)

        if form.is_valid():
            id1 = form.id1['id1']
            get_score = form.id1['score1']

            with mongodb.Mongodb() as mgd:
                mgd.update_score('articles', id1, int(get_score))
                # mgd.update_score('jie_ba_Articles', _id, get_score)
                mgd.update_modified(id1)

            return render(request, 'polls/labelfix.html')

        return render(request, 'polls/index.html', {'form': form, })


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

