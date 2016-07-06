from similarity import *

WEIGHT_TFIDF = 0.25
WEIGHT_PRICE = 0.25
WEIGHT_ORDERING = 0.25
WEIGHT_CUISINE = 0.25


def calc_r2u(user, restaurant, tfidf):
    tfidf *= WEIGHT_TFIDF
    price_sim = calc_price_sim(user['price'], restaurant['price']) * WEIGHT_PRICE
    ordering_sim = calc_ordering_sim(user['ordering'], restaurant['ordering']) * WEIGHT_ORDERING
    cuisine_sim = calc_cuisine_sim(user['cuisine'], restaurant['cuisine']) * WEIGHT_CUISINE
    return tfidf + price_sim + ordering_sim + cuisine_sim


def calc_price_sim(user, restaurant):
    return similarity(user, restaurant)


def calc_ordering_sim(user, restaurant):
    return similarity(user, restaurant)


def calc_cuisine_sim(user, restaurant):
    return similarity(user, restaurant)
