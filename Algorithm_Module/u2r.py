from similarity import *

# WEIGHT_TFIDF = 0.25
# WEIGHT_PRICE = 0.25
# WEIGHT_ORDERING = 0.25
# WEIGHT_CUISINE = 0.25


def calc_u2r(user, restaurant, tfidf, weight):
    tfidf *= weight["tfidf"]
    price_sim = calc_price_sim(user['price'], restaurant['price']) * weight["price"]
    ordering_sim = calc_ordering_sim(user['ordering'], restaurant['ordering']) * weight["ordering"]
    cuisine_sim = calc_cuisine_sim(user['cuisine'], restaurant['cuisine']) * weight["cuisine"]
    return tfidf + price_sim + ordering_sim + cuisine_sim


def calc_price_sim(user, restaurant):
    return similarity(user, restaurant)


def calc_ordering_sim(user, restaurant):
    return similarity(user, restaurant)


def calc_cuisine_sim(user, restaurant):
    return similarity(user, restaurant)
