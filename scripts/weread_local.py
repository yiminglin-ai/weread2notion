import argparse
import requests
from readwise import Readwise
from weread import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("weread_cookie")
    parser.add_argument("notion_token")
    parser.add_argument("readwise_token")
    parser.add_argument("database_id")
    parser.add_argument("ref")
    parser.add_argument("repository")
    parser.add_argument("--styles", nargs="+", type=int, help="划线样式")
    parser.add_argument("--colors", nargs="+", type=int, help="划线颜色")
    options = parser.parse_args()
    weread_cookie = options.weread_cookie
    database_id = options.database_id
    notion_token = options.notion_token
    ref = options.ref
    branch = ref.split("/")[-1]
    repository = options.repository
    styles = options.styles
    colors = options.colors
    session = requests.Session()
    session.cookies = parse_cookie_string(weread_cookie)
    # client = Client(auth=notion_token, log_level=logging.ERROR)
    session.get(WEREAD_URL)
    # latest_sort = get_sort()
    books = get_notebooklist()
    readwise_client = Readwise(options.readwise_token)
    rw_highlights = []
    if books != None:
        for index, book in enumerate(books):
            sort = book["sort"]
            # if sort <= latest_sort:
            #     continue
            book = book.get("book")
            title = book.get("title")
            cover = book.get("cover")
            if book.get("author") == "公众号" and book.get("cover").endswith(
                    "/0"):
                cover += ".jpg"
            if cover.startswith("http") and not cover.endswith(".jpg"):
                path = download_image(cover)
                cover = (
                    f"https://raw.githubusercontent.com/{repository}/{branch}/{path}"
                )
            bookId = book.get("bookId")
            author = book.get("author")
            categories = book.get("categories")
            if categories != None:
                categories = [x["title"] for x in categories]
            print(f"正在同步 {title} ,一共{len(books)}本，当前是第{index+1}本。")
            chapter = get_chapter_info(bookId)
            bookmark_list = get_bookmark_list(bookId)
            summary, reviews = get_review_list(bookId)
            bookmark_list.extend(reviews)
            bookmark_list = sorted(
                bookmark_list,
                key=lambda x: (
                    x.get("chapterUid", 1),
                    0 if (x.get("range", "") == "" or x.get("range").split("-")
                          [0] == "") else int(x.get("range").split("-")[0]),
                ),
            )
            # children, grandchild = get_children(chapter, summary, bookmark_list)
            # results = add_children(id, children)
            # if len(grandchild) > 0 and results != None:
            #     add_grandchild(grandchild, results)
            rw_highlights.extend(
                readwise_client.convert_weread_hilights_to_readwise(
                    title=title,
                    author=author,
                    chapter=chapter,
                    bookmark_list=bookmark_list,
                    source_url=
                    f"https://weread.qq.com/web/reader/{calculate_book_str_id(bookId)}",
                    cover=cover,
                ))
    if rw_highlights:
        print(rw_highlights[0])
        readwise_client.create_highlights(rw_highlights)
