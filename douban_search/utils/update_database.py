import threading
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from django.db.models import F
from harvesttext import HarvestText
from .crawler_douban import get_movies, get_reviews, get_short_comments
from douban_search.models import Comment, Keyword, Movie, Keyword_Info
import concurrent.futures
from functools import partial
from tqdm import tqdm

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
        Comment(text=ht.clean_text(data.string, norm_html=True),
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


def add_emotion_comment(comment):
    emotion = ht.analyse_sent(comment.text)
    comment.emotion = emotion
    comment.save()


def add_emotion_keyword(keyword, sent_dict):
    try:
        emotion = sent_dict[keyword.keyword]
        keyword.emotion = emotion
        keyword.save()
    except KeyError as e:
        pass


def update_emotions():
    comments = Comment.objects.all()
    docs = [i.text for i in comments]
    sent_dict = ht.build_sent_dict(docs, min_times=1, scale="+-1")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        process_comment_partial = partial(add_emotion_comment)

        with tqdm(total=len(comments)) as pbar:
            futures = []
            for comment in comments:
                future = executor.submit(process_comment_partial, comment)
                future.add_done_callback(lambda p: pbar.update())  # Update progress bar on callback
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                future.result()

        keywords = Keyword.objects.all()
        process_keyword_partial = partial(add_emotion_keyword)
        with tqdm(total=len(keywords)) as pbar:
            futures = []
            for keyword in keywords:
                future = executor.submit(process_keyword_partial, keyword, sent_dict)
                future.add_done_callback(lambda p: pbar.update())  # Update progress bar on callback
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                future.result()


def clean_comments():
    comments = Comment.objects.all()
    for comment in comments:
        comment.text = ht.clean_text(comment.text, norm_html=True)
        comment.save()


def update_counts(review_keywords=15, comment_keywords=10):
    comments = Comment.objects.all()
    total_comments = len(comments)
    with tqdm(total=total_comments, desc="Processing Comments") as pbar:
        for comment in comments:
            movie = comment.movie
            keywords = ht.extract_keywords(comment.text,
                                           review_keywords if comment.is_review else comment_keywords,
                                           method="jieba_tfidf")
            for keyword in keywords:
                keyword = Keyword.objects.get(keyword=keyword)
                try:
                    info = Keyword_Info.objects.filter(keyword=keyword, movie=movie)[0]
                    info.count += 1
                    info.save()
                except IndexError:
                    info = Keyword_Info(movie=movie, keyword=keyword)
                    info.save()
            pbar.update(1)


def translate_chinese_to_english(keyword: Keyword):
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")

    model.to('cuda')
    inputs = tokenizer.encode(keyword.keyword, return_tensors="pt")

    inputs = inputs.to('cuda')

    with torch.no_grad():
        translation = model.generate(inputs, max_length=128, num_beams=4, early_stopping=True)

    translated_text = tokenizer.decode(translation[0], skip_special_tokens=True)

    keyword.keyword2 = translated_text
    keyword.save()


def translate_keywords():
    texts = Keyword.objects.filter(keyword2__isnull=True).order_by('-count')

    with tqdm(total=len(texts)) as pbar:
        index = 0
        while index < len(texts):
            i = 0
            chinese_texts = []
            threads = []
            while i < 20:
                try:
                    t = texts[index]
                except IndexError:
                    pass
                index += 1
                if t.keyword2 is None:
                    chinese_texts.append(t)
                    t.keyword2 = 'processing'
                    t.save()
                    i += 1

                pbar.update(1)

            for text in chinese_texts:
                thread = threading.Thread(target=translate_chinese_to_english, args=(text,))
                threads.append(thread)
                thread.start()

                # 等待所有线程完成

                for thread in threads:
                    thread.join()


def clear_table_data(model):
    try:
        model.objects.all().delete()
        print("数据表数据已成功清除。")
    except Exception as e:
        print("清除数据时出现错误：", str(e))


def main():
    clear_table_data(Keyword_Info)
    clear_table_data(Keyword)
    clear_table_data(Movie)
    clear_table_data(Comment)
    update_short_comments(num_comments=20, num_movies=10, num_keywords=10)
    update_reviews(num_reviews=10, num_movies=10, num_keywords=20)
    update_counts()
    translate_keywords()


if __name__ == '__main__':
    main()
