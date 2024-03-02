import json
import shutil
from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.request import urlretrieve
from os import makedirs
import os.path, time, re

test_files = {}


def enum_links(html, base):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("link[rel='stylesheet']")
    links += soup.select("a[href]")
    result = []

    for a in links:
        href = a.attrs["href"]
        url = urljoin(base, href)
        result.append(url)
    return result


def download_file(url):
    o = urlparse(url)
    savepath = "./" + o.netloc + o.path
    if re.search(r"/$", savepath):
        savepath += "index.html"
    savedir = os.path.dirname(savepath)

    if os.path.exists(savepath):
        return savepath

    if not os.path.exists(savedir):
        makedirs(savedir)

    try:
        urlretrieve(url, savepath)
        time.sleep(1)
        return savepath
    except:
        print("ダウンロード失敗:", url)
        return None


def search_posts(html: str):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select(".thread-title")[0].contents[0]

    if "⍰" in title:
        title = "バグスレ"

    posts = soup.select("li.post")
    post_datas = []
    for post in posts:
        id = post.get("id")
        name = [content.text for content in post.select_one(".handle-name").contents][0]
        timestamp = [content.text for content in post.select_one(".timestamp").contents][0]
        body = [content.text for content in post.select_one(".post-body").contents]
        post_data = {"id": id, "name": name, "timestamp": timestamp, "body": body}
        post_data = f"id: {id}	投稿者:{name}	投稿日時: {timestamp[2:].strip()}	{''.join(body)}"
        post_datas.append(post_data)
    return title, post_datas


def analize_html(url, root_url):
    savepath = download_file(url)
    if savepath is None:
        return
    if savepath in test_files:
        return
    test_files[savepath] = True
    print("analize_html=", url)

    html = open(savepath, "r", encoding="utf-8").read()
    links = enum_links(html, url)
    if re.search(r"[0-9][0-9]/$", url):
        title, posts = search_posts(html)
        with open(f"./posts/{title}", "w") as f:
            f.write("\n".join(posts))

    for link_url in links:
        if link_url.find(root_url) != 0:
            if not re.search(r".css$", link_url):
                continue

        analize_html(link_url, root_url)
        download_file(link_url)


if __name__ == "__main__":
    url = "https://highconsciouslab.com/jr6p5zrg5uv4up5a0pv5h06n1/"
    if os.path.exists("highconsciouslab.com"):
        shutil.rmtree("highconsciouslab.com")
    if os.path.exists("./posts"):
        shutil.rmtree("./posts")
    os.mkdir("./posts")

    analize_html(url, url)
