from django.db import models


# Create your models here.
class Tour(models.Model):
    """Таблица экскурсий"""

    guide = models.ForeignKey('tours.Guide', on_delete=models.SET_NULL, null=True)
    provider = models.ForeignKey('tours_parser.ToursProviders', on_delete=models.SET_NULL, null=True)

    name = models.CharField("Название экскурсии", max_length=32)
    description = models.TextField()
    price = models.DecimalField("Цена", decimal_places=2, max_digits=6, null=True)
    price_on_request = models.BooleanField('Цена по запросу', default=False)
    duration = models.PositiveIntegerField('Длительность, мин.', default=0)

    def __str__(self):
        return f"{self.name} {self.price} руб. / {self.duration} мин."


class Guide(models.Model):
    """Таблица гидов."""

    fio = models.CharField('ФИО гида.', max_length=64)
    phone = models.CharField('Телефон гида', max_length=16)

    def __str__(self):
        return f"{self.fio} ({self.phone})"


class Schedule(models.Model):
    """Расписание туров"""

    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    start_location = models.TextField()

    def __str__(self):
        admin_format = '%d %B, %H:%M'
        return f"{self.tour.name} {self.start_time.strftime(admin_format)} от {self.start_location}"


