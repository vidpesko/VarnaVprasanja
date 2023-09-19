from .views import all_questions, vehicle_selection, convert_db

from django.urls import path, include


urlpatterns = [
    path('izberi/', vehicle_selection, name='vehicle_selection'),
    path('vprašanja/<str:vehicle>', all_questions, name='questions'),
    path('convert/', convert_db, name='convert'),
]
