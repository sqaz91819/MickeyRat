from django.db import models
from django.utils import timezone
import datetime

# Create your models here.


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Query(models.Model):
    query = models.CharField(max_length=80, primary_key=True)

    def is_valid(self):
        if self.query['search']:
            return True
        else:
            return False

    def __str__(self):
        return self.query


class ScoreMovie(models.Model):
    score = models.IntegerField(default=1)
    movie = models.CharField(max_length=80, primary_key=True)

    def is_valid(self):
        if self.score['score2'] and self.score['movie2']:
            return True
        else:
            return False

    def __str__(self):
        return self.movie
