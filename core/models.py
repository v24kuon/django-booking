
from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=10)
    floor = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
