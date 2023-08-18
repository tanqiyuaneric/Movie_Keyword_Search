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
    keywords = models.ForeignKey(Keyword, on_delete=models.PROTECT, null=True)
    url = models.URLField()

    def __str__(self):
        return self.name


class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    text = models.TextField()
    is_review = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:5]+'...'
