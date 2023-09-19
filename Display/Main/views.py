from .models import Question, Vehicle

from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
import os


# Create your views here.
def vehicle_selection(request):
    context = {}

    # ? Get all vehicles
    vehicles = Vehicle.objects.all()
    context['vehicles'] = vehicles

    return render(request, 'Main/vehicle_selection.html', context=context)


def all_questions(request, vehicle):
    context = {}

    # ? Getting info about vehicle
    vehicle = Vehicle.objects.get(url_name=vehicle)
    context['vehicle'] = vehicle

    # ? Getting questions
    q_path = os.getcwd() + '/Temporary/questions.json'
    with open(q_path) as q:
        questions = json.load(q)['questions']

        num_of_questions = len(questions)
        # ? Pagginating
        paginator = Paginator(questions, 20)
        page = request.GET.get('page', 1)

        try:
            print(page)
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        context['questions'] = questions
        context['num_of_questions'] = num_of_questions


    return render(request, 'Main/questions.html', context=context)

def convert_db(request):
    questions_path = os.getcwd() + '/Temporary/questions.json'
    with open(questions_path) as questions:
        questions = json.load(questions)['questions']

        for question in questions:
            points = question['info']['points']

            q_text = question['content']['questions_text']
            q_img = question['content']['image_link']
            q_type = question['content']['type']

            answers = question['content']['answers']
            r_answers = question['content']['right_answers']
            r_answer_full = question['content']['right_answer_response']

            new_q = Question.objects.create(question_text=q_text, points=points, question_type=q_type, image_path=q_img, right_answer_full=r_answer_full)

            new_q.store_answers(answers)
            new_q.store_right_answers(r_answers)
            new_q.save()
    return HttpResponse('Converting done!')