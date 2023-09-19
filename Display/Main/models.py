from django.db import models


# Create your models here.
class Question(models.Model):
    question_text = models.TextField()

    points = models.IntegerField()
    question_type = models.CharField(max_length=30)
    image_path = models.CharField(max_length=50, blank=True)

    answers = models.TextField(null=True)
    righ_answers = models.TextField(null=True)
    right_answer_full = models.TextField()

    def store_answers(self, answers):
        self.answers = '§'.join(answers)
    
    def get_answers(self):
        return self.answers.split('§')

    def store_right_answers(self, r_answers):
        self.righ_answers = '§'.join([str(a) for a in r_answers])
    
    def get_right_answers(self):
        return [int(a) for a in self.righ_answers.split('§')]
    
    def __str__(self) -> str:
        return self.question_text


class Vehicle(models.Model):
    name = models.CharField(max_length=40)
    category = models.TextField(null=True)
    description = models.CharField(max_length=50)
    url_name = models.CharField(max_length=50)

    icon_path = models.CharField(max_length=40)

    def store_categories(self, categories):
        self.category = '§'.join([str(a) for a in categories])
    
    def get_categories(self):
        return self.category.split('§')