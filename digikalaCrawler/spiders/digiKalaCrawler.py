# -*- coding: utf-8 -*-
import scrapy
import cssutils
   
class digikalaCrawler(scrapy.Spider):
    name = "digikalaCrawler"
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
    }
    
    def start_requests(self):
        urls = [
            'https://www.digikala.com'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #response.url.split("/")[-2]
        page = 'main'
        filename = '%s.txt' % page
        subcat_lis = response.css('.c-navi-new-list__sublist-option--title')
        hrefs = subcat_lis.css('a.c-navi-new__big-display-title::attr("href")').getall() 
        yield response.follow(hrefs[0], self.get_products_info)
#        with open(filename, 'wb') as f:
#            f.write(response.body)
#        self.log('Saved file %s' % filename)
        
        
        
        
        
        
        
#   input: response [html] (new page)
#   output: [
#               {
#                       product_id: 0,
#                       product_name: product_Names[0],
#                       star_rating: 74.4%,
#                       npVoted: 165,
#                       Price: 170000,
#                       urlLinkTo: ‘’,
#               }
#               {
#                       product_id: 1,
#                       productName: product_titles[1],
#                       starRating: 74.4%,
#                       npVoted: 165,
#                       Price: 170000,
#                       urlLinkTo: ‘’,
#               }, ...
#           ]
    def get_products_info(self, response):
        product_box_content_div = response.css('.c-product-box__content')
        product_names = product_box_content_div.css('.c-product-box__title').xpath('./a/text()').getall()
        star_ratings_style = product_box_content_div.css('.c-product-box__rate-comparision').css('.c-stars-plp__selected').xpath('@style').getall()
        
        star_ratings = list()
        for css in star_ratings_style:
            parsed_css = cssutils.parseStyle(str(css))
            for each in parsed_css:
                star_ratings.append(each.value)
        
        
        
        if len(product_names) == 36:
            print("product_names == 36")
        if len(star_ratings) == 36:
            print("star_ratings == 36")




#    input: url/?pageno=i
#    output: {
#                isnextpage: true|false,
#                nextpage: htmltoparse
#                
#            }
    def nextPage(self, url, pageno = 1):
        pass







#    input: output from get_products_urls
#    output: final .csv file
    def parse_products_urls(self):
        pass
    

    

#import scrapy
#
#
#class AuthorSpider(scrapy.Spider):
#    name = 'author'
#
#    start_urls = ['http://quotes.toscrape.com/']
#
#    def parse(self, response):
#        # follow links to author pages
#        for href in response.css('.author + a::attr(href)'):
#            yield response.follow(href, self.parse_author)
#
#        # follow pagination links
#        for href in response.css('li.next a::attr(href)'):
#            yield response.follow(href, self.parse)
#
#    def parse_author(self, response):
#        def extract_with_css(query):
#            return response.css(query).get(default='').strip()
#
#        yield {
#            'name': extract_with_css('h3.author-title::text'),
#            'birthdate': extract_with_css('.author-born-date::text'),
#            'bio': extract_with_css('.author-description::text'),
#        }
#    
