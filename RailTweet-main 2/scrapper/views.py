from django.shortcuts import render, redirect
import requests
import re

from bs4 import BeautifulSoup
from . import models

def iceland(request):
    template = 'dashboard/scrapper/iceland/index.html'

    return render(request, template, {})


def scrap_data(url, new_req):
    
    page_source = requests.get(url)
    soup = BeautifulSoup(page_source.content, 'html.parser')
    base_url = soup.select_one('.primary-logo a')['href']
    
    product_name = soup.select_one('.product-name').text
    price = soup.select_one('.product-sales-price span').text

    reviews = []
    review_pages = soup.select_one('.showMore')

    if not review_pages:
        extract_reviews(soup, reviews)
        return Product(product_name, price, len(reviews), reviews, url)

    for page in range(int(review_pages['data-maxpage'])+1):
        review_link = f"{base_url}{soup.select_one('.showMore')['data-url']}&page={page}"
        print("Extract reviews from", review_link)
        review_ps = requests.get(review_link)
        review_soup = BeautifulSoup(review_ps.content, 'html.parser')

        extract_reviews(review_soup, reviews)
    
    total_reviews = len(reviews)

    #print(product_name, price, total_reviews, reviews, url)
    for review in reviews:
            new_pr = models.ProductReview(
                request = new_req,
                name = product_name,
                price = price,
                total_reviews = total_reviews,
                review_date =  review['review_date'],
                reviewer_name =  review['reviewer_name'],
                review_comment =  review['review_comment'],
                review_stars =  review['review_stars'],
                url = url
            )

            new_pr.save()

    return 0


def extract_reviews(soup, reviews=[]):
    for review in soup.select('.feefoReview'):
        review_detail = review.select_one('.submitted').text
        review_comment = review.select('p')[-1].text
        review_stars = len(review.select('.review-star-fill')) + (len(review.select('.review-star-half'))/2)

        reviews.append({
            'reviewer_name': re.findall(r'by (.*?) on', review_detail)[0],
            'review_date': review_detail.split(' ')[-1],
            'review_comment':review_comment,
            'review_stars':review_stars
            })