# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import DigikalacrawlerItem

class digikalaCrawler(scrapy.Spider):
    name = "digikalaCrawler"
    allowed_domains = ["www.digikala.com"]
    # splash_meta = {'splash': {'endpoint': 'execute', 'args': {'wait': 5, 'lua_source': self.script}}}
    # custom_settings = {
    #     'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
    # }
    def start_requests(self):
        urls = [
            'https://www.digikala.com'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        subcat_lis = response.css('.c-navi-new-list__sublist-option--title')
        rel_cat_urls = subcat_lis.css('a.c-navi-new__big-display-title::attr("href")').getall()
        for each_url in rel_cat_urls:
            next_category_url = response.urljoin(each_url).split("?")[0]
            yield scrapy.Request(url = next_category_url, callback = self.get_products_list, meta={'list_page': 1})
        
        # # Rare ones
        # next_category_url = response.urljoin(rel_cat_urls[99]).split("?")[0]
        # yield scrapy.Request(url = next_category_url, callback = self.get_products_list)



    #   input: response [html] (new page)
    #   output: [
    #               {
    #                       product_id: 0,
    #                       product_name: product_Names[0],
    #                       star_rating: 74.4%,
    #                       n_peaple_voted: 165,
    #                       Price: 170000,
    #                       urlLinkTo: ‘’,
    #               }
    #               {
    #                       product_id: 1,
    #                       productName: product_titles[1],
    #                       star_rating: 74.4%,
    #                       npVoted: 165,
    #                       Price: 170000,
    #                       urlLinkTo: ‘’,
    #               }, ...
    #           ]
    def get_products_list(self, response):
        product_box_content_div = response.css('.c-product-box__content')
        if product_box_content_div:
            for eachproduct in product_box_content_div:
                items = DigikalacrawlerItem()
                # check if product id recorded for this product
                if self.is_child_node_exist(eachproduct.xpath('.//div[contains(@class, "c-product-box__title")]'), 'a'):
                    # Store in dictionary
                    product_id = eachproduct.xpath(
                        './/div[contains(@class, "c-product-box__title")]').css('a::attr(data-adro-ad-click-id)').get()
                    items['product_id'] = product_id
                else:
                    # Store Unknown in dictionary
                    items['product_id'] = 'Unknown'

                # check if product name recorded for this product
                if self.is_child_node_exist(eachproduct.css('.c-product-box__title'), 'a'):
                    # Store in dictionary
                    product_name = eachproduct.css(
                        '.c-product-box__title').xpath('./a/text()').get()
                    items['product_title'] = product_name
                else:
                    items['product_title'] = 'Unknown'

                # check if star rating recorded for this product
                if self.is_child_node_exist(eachproduct.css('.c-product-box__rate-comparision'), 'div'):
                    # Store in dictionary
                    rate = 0
                    width_attr_str = eachproduct.css(
                        '.c-product-box__rate-comparision').css('.c-stars-plp__selected').xpath('@style').get()
                    rate = str.strip(width_attr_str.split(':')[1])
                    items['star_rating'] = float(rate.split('%')[0])
                else:
                    items['star_rating'] = 'Unknown'

                # check if npVotes recorded for this product
                if self.is_child_node_exist(eachproduct.css('.c-product-box__rate-comparision'), 'div'):
                    npVotes = 0
                    npVotes_str = eachproduct.css(
                        '.c-product-box__rate-comparision--rate-people::text').get()
                    ls = npVotes_str.split()
                    for s in ls:
                        ds = s.split(',')
                        s = ''.join(ds)
                        if s.isdigit():
                            npVotes = int(s)
                    items['n_peaple_voted'] = npVotes
                else:
                    items['n_peaple_voted'] = 'Unknown'

                # check if price recorded for this product
                if self.is_child_node_exist(eachproduct.xpath('.//div[contains(@class, "c-price__value c-price__value--plp")]'), 'div'):
                    price = 0
                    price_str = eachproduct.xpath('.//div[contains(@class, "c-price__value c-price__value--plp")]').xpath(
                        './/div[contains(@class, "c-price__value-wrapper")]/text()').get()
                    ls = price_str.split()
                    for s in ls:
                        ds = s.split(',')
                        s = ''.join(ds)
                        if s.isdigit():
                            price = int(s)
                    items['price'] = price
                else:
                    items['price'] = 'Unknown'

                # check if linkTo provided for this product
                if self.is_child_node_exist(eachproduct.css('.c-product-box__title'), 'a'):
                    rel_linkto_details = eachproduct.xpath('.//div[contains(@class, "c-product-box__title")]').css('a::attr(href)').get()
                    abs_linkto_details = response.urljoin(rel_linkto_details)
                    items['linkto'] = abs_linkto_details
                    yield scrapy.Request(url = abs_linkto_details ,callback=self.go_to_product_details, meta={'product_general_info': items, 'abs_link': abs_linkto_details, 'comments_page': 1, 'comments_list': [], 'flg': 1})
                else:
                    items["n_peaple_Recommended"] = "Unknown"
                    items["brand"] = "brand"
                    items["cat"] = "Unknown"
                    items["overview"] = "Unknown"
                    items["comments"] = []
                    yield items
            
            # Go To Next Page
            # if there is a new page to crawl go for it
            nextpage_url = self.list_nextpage(response.url)
            yield scrapy.Request(url=nextpage_url, callback=self.get_products_list)
        else:
            # there is no page to crawl for this category. Go to the next Category
            return

    def go_to_product_details(self, response):
        items = response.meta.get("product_general_info")
        comments_data = response.meta.get('com_data')
        # Get product title, brand, overview and number of recommendations
        if response.css('.c-product__title'):
            # Get Overview of the product if exists
            overviewSection = response.css(".c-content-expert__summary")
            if overviewSection:
                items["overview"] = overviewSection.xpath('.//div[contains(@class, "c-mask js-mask")]').get()
            else:
                items["overview"] = "Unknown"
            # Get Number_of_people_recommended item if exists
            if response.css('.c-product__guaranteed span::text'):
                snumrec = response.css('.c-product__guaranteed span::text').re(r'\d+')
                items["n_peaple_Recommended"] = int(snumrec[0])
            else:
                items["n_peaple_Recommended"] = "Unknown"
            
            # Get Brand
            if response.css(".product-brand-title::text"):
                items["brand"] = response.css(".product-brand-title::text").get()
            else:
                items["brand"] = "Unknown"
        
            # Get Category
            if response.css(".c-product__directory li+ li .btn-link-spoiler::text"):
                items["cat"] = response.css(".c-product__directory li+ li .btn-link-spoiler::text").get()
            else:
                items["cat"] = "Unknown"
            product_id = items["product_id"]
            abs_link_to_comments = f'https://www.digikala.com/ajax/product/comments/{product_id}/?page=1&mode=buyers'
            yield scrapy.Request(url = abs_link_to_comments, callback=self.go_to_product_details, meta={'product_general_info': items, 'com_data': []})
        # check to see if any review exist for this product
        elif response.css(".c-comments__list"):
            # Get the Number of comments for this page
            n_of_comments = response.xpath('.//div[contains(@class, "c-comments__likes js-comment-like-container")]')
            for eachComment in range(len(n_of_comments)):
                comment = {}
                eachComment = eachComment + 1
                # Get isbuyer and
                # Get if this product recommended by the reviewer
                if response.css(f'li:nth-child({eachComment}) .aside'):
                    if response.css(f'li:nth-child({eachComment}) .c-message-light--purchased::text'):
                        comment["is_buyer"] = 1
                    else:
                        comment["is_buyer"] = 0

                    if response.css(f'li:nth-child({eachComment}) .c-message-light--opinion-negative'):
                        comment["recommended"] = -1
                    elif response.css(f'li:nth-child({eachComment}) .c-message-light--opinion-positive'):
                        comment["recommended"] = 1
                    elif response.css(f'li:nth-child({eachComment}) .c-message-light--opinion-noidea'):
                        comment["recommended"] = 0
                    else:
                        comment["recommended"] = "Unknown"
                else:
                    comment["is_buyer"] = "Unknown"
                    comment["recommended"] = "Unknown"
                
                if response.css(f"li:nth-child({eachComment}) .article"):
                    # Get Comment Title 
                    if response.css(f'li:nth-child({eachComment}) .header div::text'):
                        comment["comment_title"] = response.css(f'li:nth-child({eachComment}) .header div::text').get()
                    else:
                        comment["comment_title"] = "Unknown"
                        
                # Get Comment
                if response.css(f'li:nth-child({eachComment}) div.article p'):
                    comment['review'] = response.css(f'li:nth-child({eachComment}) div.article p').get()
                else:
                    comment['review'] = "Unknown"
                # Get number of likes for a comment
                comment["c-likes"] = int(response.css(f'li:nth-child({eachComment}) .js-comment-like').css('button::attr(data-counter)').get())
                # Get number of dislikes for a comment
                comment["c-dislikes"] = int(response.css(f'li:nth-child({eachComment}) .js-comment-dislike').css('button::attr(data-counter)').get())

                # Get advantages
                if response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-positive span::text'):
                    if len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-positive li')) == 1:
                        comment["advantages"] = response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-positive ul li::text').get()
                    elif len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-positive li')) > 1:
                        comment["advantages"] = len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-positive li'))
                else:
                    comment["advantages"] = "Unknown"
                # Get disadvantages
                if response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-negative span::text'):
                    if len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-negative li')) == 1:
                        comment["disadvantages"] = response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-negative ul li::text').get()
                    elif len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-negative li')) > 1:
                        comment["disadvantages"] = len(response.css(f'li:nth-child({eachComment}) .c-comments__evaluation-negative li'))
                else:
                    comment["disadvantages"] = "Unknown"
                
                # Append To list
                comments_data.append(comment)

            items["comments"] = comments_data
            # Go To The Next Page
            pID = items["product_id"]
            link_to_next_comment_page = self.comments_nextpage(response.url, pID)
            yield scrapy.Request(url = link_to_next_comment_page ,callback=self.go_to_product_details, meta={'product_general_info': items, 'com_data': comments_data})
        else:
            # there is no commetns section for this product (may be first page or last page + 1)
            yield items

    # input: response
    # output: url of the next page
    def list_nextpage(self, url):
        if re.findall(r'pageno=\d+', url):
            nxt_url = url.split('?')
            pageorder = nxt_url[1]
            page = re.findall(r'pageno=\d+', pageorder)
            pageno = int(page[0].split('=')[1])
            pageno = pageno + 1
            nextpage_url = f'{nxt_url[0]}?pageno={pageno}'
            return nextpage_url
        else:
            pageno = 2
            nextpage_url = f'{url}?pageno={pageno}'
            return nextpage_url

    # input: response
    # output: url of the next page for comments
    def comments_nextpage(self, url, pID):
        if re.findall(r'page=\d+', url):
            nxt_url = url.split('?')
            pageorder = nxt_url[1]
            page = re.findall(r'page=\d+', pageorder)
            pageno = int(page[0].split('=')[1])
            pageno = pageno + 1
            nextpage_url = f'https://www.digikala.com/ajax/product/comments/{pID}/?page={pageno}&mode=buyers'
            return nextpage_url
        else:
            return f'https://www.digikala.com/ajax/product/comments/{pID}/?page={10000}&mode=buyers'


    # input: <parent div> and type of the tag (<div> or <a> or ...)
    # output: boolean
    def is_child_node_exist(self, parent, childtype):
        s = f'./{str(childtype)}'
        if(parent.xpath(s).get() is None):
            return False
        else:
            return True