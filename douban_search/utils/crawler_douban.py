import json
import urllib
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
import re
from harvesttext import HarvestText

ht = HarvestText()


def ask_url(url: str) -> str:
    head = {
        "User-Agent":
            "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / "
            "89.0.4389.90Safari / 537.36Edg / 89.0.774.63 ",
        "Cookie":
            'bid=M_6JtQ6VU54; _pk_id.100001.4cf6=a90ccbc4e91ed3b4.1692255979.; __utmc=30149280; __utmc=223695111; '
            'll="108288"; __yadk_uid=z0mtFkVtA8WOrNyakUdnu8d4tmLPWnCo; '
            '_vwo_uuid_v2=DA65B61765611CC1C57FAD43579751E1A|cf9a2c5e50c39581682cf45add635ca2; '
            'dbcl2="273496291:rZg9DXAaof8"; ck=wBzJ; '
            '_pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1692284313%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; '
            '_pk_ses.100001.4cf6=1; ap_v=0,6.0; __utma=30149280.1687238511.1692255980.1692262491.1692284317.4; '
            '__utmb=30149280.0.10.1692284317; __utmz=30149280.1692284317.4.2.utmcsr=accounts.douban.com|utmccn=('
            'referral)|utmcmd=referral|utmcct=/; __utma=223695111.2004535303.1692255980.1692262491.1692284317.4; '
            '__utmb=223695111.0.10.1692284317; __utmz=223695111.1692284317.4.2.utmcsr=accounts.douban.com|utmccn=('
            'referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0'
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


def get_short_comments(movie_index: str) -> str or None:
    index = 0
    while True:
        url = f'https://movie.douban.com/subject/{movie_index}/comments?start={index}&limit=20&status=P&sort=new_score'
        index += 20
        html = ask_url(url)
        soup = BeautifulSoup(html, "html.parser")
        page_elements = soup.find_all('span', class_='short')
        if len(page_elements) == 0:
            return None
        pattern = re.compile(r'>(.*?)<')
        for element in page_elements:
            comments = re.findall(pattern, str(element))
            if len(comments) > 0:
                for comment in comments:
                    if len(comment) > 0:
                        yield comment


def get_reviews(movie_index:str) -> str or None:
    index = 0
    while True:
        url = f'https://movie.douban.com/subject/{movie_index}/reviews?start={index}'
        index += 20
        html = ask_url(url)
        soup = BeautifulSoup(html, "html.parser")
        page_elements = soup.find_all('a', class_='unfold')
        if len(page_elements) == 0:
            return None
        pattern = re.compile(r'-(.*?)-')
        for element in page_elements:
            try:
                review_id = re.findall(pattern, element.get('id'))[0]
            except IndexError:
                continue
            json_data = ask_url(f'https://movie.douban.com/j/review/{review_id}/full')
            data = json.loads(json_data)
            review = data['html']
            yield review.replace('<br>', '\n')


def get_movies() -> str or None:
    index = 0
    while True:
        url = f'https://movie.douban.com/top250?start={index}&filter='
        index += 20
        html = ask_url(url)
        soup = BeautifulSoup(html, "html.parser")
        page_elements = soup.find_all('div', class_='hd')
        if len(page_elements) == 0:
            return None
        pattern_id = re.compile(r'/subject/(\d+)/"')
        pattern_name2 = re.compile(r' / (.*)')
        for element in page_elements:
            name_soup = BeautifulSoup(str(element), "html.parser")
            try:
                movie_id = re.findall(pattern_id, str(element))[0]
                name1 = name_soup.find_all('span', class_='title')[0].getText()
            except IndexError:
                continue
            try:
                name2 = name_soup.find_all('span', class_='title')[1].getText()
                name2 = re.findall(pattern_name2, name2)[0]
            except IndexError:
                name2 = None
            yield movie_id, name1, name2


# 保存评论到文件
def save_to_file(filename, comment):
    with open(filename, 'a', encoding='utf-8') as file:
        try:
            file.write(comment + '\n')
        except UnicodeEncodeError:
            print(f'failed to write {comment}')


def main():
    filename = 'comments.txt'
    comments = get_short_comments('1291546')
    while True:
        comment = next(comments)
        if comment:
            save_to_file(filename, comment)
        else:
            break


if __name__ == '__main__':
    a = get_movies()
    print(next(a))
    print(next(a))
