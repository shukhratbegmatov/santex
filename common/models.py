from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, null=True)
    region = models.ForeignKey("common.Region", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name
