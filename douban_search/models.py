from django.db import models


# Create your models here.
class Keyword(models.Model):
    keyword = models.CharField(max_length=250)
    count = models.IntegerField(default=1)

    def __str__(self):
        return self.keyword


class Movie(models.Model):
    name1 = models.CharField(max_length=250)
    name2 = models.CharField(max_length=250, null=True)
    year = models.IntegerField(null=True)
    img = models.ImageField(upload_to="gallery", null=True)
    keywords = models.ManyToManyField(Keyword)
    url = models.URLField()

    def __str__(self):
        return self.name1


class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    text = models.TextField()
    emotion = models.FloatField()
    is_review = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:5]+'...'
