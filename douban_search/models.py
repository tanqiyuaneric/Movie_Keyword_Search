from django.db import models


# Create your models here.
class Keyword(models.Model):
    keyword = models.CharField(max_length=250)

    def __str__(self):
        return self.keyword


class Movie(models.Model):
    name = models.CharField(max_length=250)
    year = models.IntegerField(null=True)
    img = models.ImageField(upload_to="gallery", null=True)
    keywords = models.ForeignKey(Keyword, on_delete=models.PROTECT)
    url = models.URLField()

    def __str__(self):
        return self.name
