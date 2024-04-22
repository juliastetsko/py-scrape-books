import scrapy
from scrapy.http import Response

NUM_DICT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> Response:
        book_links = response.css("article > h3 > a")
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        info_table = response.css(".table td::text").getall()
        return {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                "".join(char for char in info_table[5] if char.isnumeric())
            ),
            "rating": NUM_DICT[response.css(
                ".star-rating::attr(class)"
            ).get().split()[1]],
            "category": response.css(
                "ul.breadcrumb > li > a::text"
            ).getall()[-1],
            "description": response.css(".product_page > p::text").get(),
            "upc": info_table[0],
        }
