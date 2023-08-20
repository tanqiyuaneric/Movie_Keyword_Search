from django.db.models import F
from harvesttext import HarvestText
from .crawler_douban import get_movies, get_reviews, get_short_comments
from douban_search.models import Comment, Keyword, Movie

ht = HarvestText()


class Data:
    def __init__(self, string: str, keywords: list, movie_id: str, name1: str, name2: str):
        self.string = string
        self.keywords = keywords
        self.movie_id = movie_id
        self.name1 = name1
        self.name2 = name2


class Comments(Data):
    def __init__(self, string, keywords, movie_id, name1, name2):
        super().__init__(string, keywords, movie_id, name1, name2)


class Reviews(Data):
    def __init__(self, string, keywords, movie_id, name1, name2):
        super().__init__(string, keywords, movie_id, name1, name2)


def save_data(data: Data):
    for keyword in data.keywords:
        if len(Keyword.objects.filter(keyword=keyword)) == 0:
            k = Keyword(keyword=keyword)
            k.save()
        else:
            Keyword.objects.filter(keyword=keyword).update(count=F('count') + 1)

    if len(Movie.objects.filter(name1=data.name1)) == 0:
        movie = Movie(name1=data.name1,
                      name2=data.name2,
                      id=data.movie_id,
                      url=f"https://movie.douban.com/subject/{data.movie_id}/")
        movie.save()
    else:
        movie = Movie.objects.get(name1=data.name1)

    for keyword in data.keywords:
        movie.keywords.add(Keyword.objects.get(keyword=keyword))
    movie.save()

    if len(Comment.objects.filter(text=data.string)) == 0:
        Comment(text=data.string,
                is_review=True if isinstance(data, Reviews) else False,
                movie=Movie.objects.get(name1=data.name1),
                ).save()


def update_short_comments(num_movies=10, num_comments=10, num_keywords=10):
    movies = get_movies()
    for _ in range(num_movies):
        try:
            movie_id, name1, name2 = next(movies)
        except StopIteration:
            break
        comments = get_short_comments(movie_id)
        for __ in range(num_comments):
            try:
                comment = next(comments)
            except StopIteration:
                break
            keywords = ht.extract_keywords(comment, num_keywords, method="jieba_tfidf")
            data = Comments(comment, keywords, movie_id, name1, name2)
            save_data(data)


def update_reviews(num_movies=10, num_reviews=10, num_keywords=10):
    movies = get_movies()
    for _ in range(num_movies):
        try:
            movie_id, name1, name2 = next(movies)
        except StopIteration:
            break
        reviews = get_reviews(movie_id)
        for __ in range(num_reviews):
            try:
                review = next(reviews)
            except StopIteration:
                break
            keywords = ht.extract_keywords(review, num_keywords, method="jieba_tfidf")
            data = Reviews(review, keywords, movie_id, name1, name2)
            save_data(data)


def update_emotions():
    comments = Comment.objects.all()
    docs = [i.string for i in comments]
    ht.build_sent_dict(docs, min_times=1, scale="+-1")
    for comment in comments:
        comment.emotion = ht.analyse_sent(comment.text)
        comment.save()


def clean_comments():
    comments = Comment.objects.all()
    for comment in comments:
        comment.text = ht.clean_text(comment.text, norm_html=True)
        comment.save()


def main():
    update_short_comments(num_comments=50000, num_movies=250, num_keywords=10)
    update_reviews(num_reviews=500, num_movies=250, num_keywords=20)


if __name__ == '__main__':
    pass
