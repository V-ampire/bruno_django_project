from tours.models import Schedule


def get_full_schedule():
    schedule = Schedule.objects.select_related('tour', 'tour__guide').all()
    # Как ДЗ найти способ не вытягивать из БД лишние поля, например tour.price, tour.description и т.д.
    # for slot in schedule:
    #     print(slot.tour.name)
    # print(f">>> {str(schedule.query)}")
    return schedule
