from django.shortcuts import render

from tours.services import get_full_schedule


def get_all_tours(request):
    if request.method == 'GET':
        schedule = get_full_schedule()
        # Вернуть html со всеми турами
        return render(request, 'tours/index.html', context=dict(schedule=schedule))
