from Algorithm_Module.similarity import *


# WEIGHT_TAG = 0.25
# WEIGHT_PRICE = 0.25
# WEIGHT_ORDERING = 0.25
# WEIGHT_CUISINE = 0.25

def calc_u2u(u1, u2, weight):
    tag_sim = calc_tag_sim(u1['tags'], u2['tags']) * weight["tag"]
    price_sim = calc_price_sim(u1['price'], u2['price']) * weight["price"]
    ordering_sim = calc_ordering_sim(u1['ordering'], u2['ordering']) * weight["ordering"]
    cuisine_sim = calc_cuisine_sim(u1['cuisine'], u2['cuisine']) * weight["cuisine"]
    return tag_sim + price_sim + ordering_sim + cuisine_sim


def calc_tag_sim(u1, u2):
    counter = 0  # 計算有多少tag只屬於其中一個使用者。
    for t in u1:
        if t not in u2:
            counter += 1
    for t in u2:
        if t not in u1:
            counter += 1
    if counter == 0:
        return 1
    return 1 - (counter / (len(u1) + len(u2)))


"""
@param user price preference of user.
@param restaurant price interval of restaurant.
"""


def calc_price_sim(u1, u2):
    return similarity(u1, u2)


"""
@param user Ordering preference of user.
@param restaurant Ordering way of restaurant.
"""


def calc_ordering_sim(u1, u2):
    return similarity(u1, u2)


def calc_cuisine_sim(u1, u2):
    return similarity(u1, u2)


if __name__ == '__main__':
    from db import DBConn

    conn = DBConn()
    conn.open()  # output similarity
    users_info = conn.getUsersInfo()
    num = len(users_info)

    similarities = []
    u2u_weights = {
        'price': 0.25,
        'ordering': 0.25,
        'cuisine': 0.25,
        'tag': 0.25
    }
    for i, user1 in enumerate(users_info):
        weights = conn.getWeightWithID(user1['uid'])
        for j in range(i, num):
            user2 = users_info[j]
            sim = calc_u2u(user1, user2, u2u_weights)
            sim = sim if user1['uid'] != user2['uid'] else 1
            similarities.append((user1['uid'], user2['uid'], float(sim)))

    conn.updateU2USimilarities(similarities)
    conn.close()
