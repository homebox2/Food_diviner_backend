import json
from datetime import datetime

from flask import Flask, request, Response

from db import DBConn

WEIGHT_R2R = 0.25
WEIGHT_R2U = 0.25
WEIGHT_U2U = 0.25
WEIGHT_CONTEXT = 0.25

DEFAULT_RECENT_RESTAURANT_NUM = 3
DEFAULT_SIM_USER_NUM = 3
DEFAULT_SIM_USER_RESTAURANT_NUM = 5
application = Flask(__name__)

conn = DBConn()


@application.route("/recommendation")
def get_recommendation():
    conn.open()
    # Receive uid and optional context, such as weather and transportation.

    if 'user_id' not in request.args:
        resp = Response(status=400)
        return resp
    # 取的Request 參數
    uid = request.args['user_id']

    conn.open()
    user = conn.getUserInfoWithID(uid)
    restaurants = conn.getRestaurantsInfo()
    print("get request ", datetime.now())
    scores = {}
    for restaurant in restaurants:
        scores[restaurant['rid']] = 0  # 初始化每個餐廳的分數。
    print("init restaurant scores ", datetime.now())
    similar_users = conn.getU2USimilarities(uid, DEFAULT_SIM_USER_NUM)
    u2u_sim = {}

    for u, s in similar_users.items():  # 使用者間的相似度
        user_recent = conn.getUserActivity(u, DEFAULT_SIM_USER_RESTAURANT_NUM)  # 相近的使用者最近去過的餐廳。
        for r in user_recent:
            if r in u2u_sim:
                u2u_sim[r] += s
            else:
                u2u_sim[r] = s

    for r, s in u2u_sim:
        # 正規化餐廳分數並乘以u2u的權重。
        scores[r] += s / DEFAULT_SIM_USER_NUM * WEIGHT_U2U

    print("figure out u2u ", datetime.now())
    # 找出和使用者最近去過的餐廳相似的餐廳。
    recent_restaurants = conn.getUserActivity(uid, DEFAULT_RECENT_RESTAURANT_NUM)
    r2r_sim = {}
    for recent in recent_restaurants:
        sim = conn.getR2RSimilarities(recent)
        for r, s in sim.items():
            if r in r2r_sim:
                r2r_sim[r] += s
            else:
                r2r_sim[r] = s
    for k, v in r2r_sim.items():
        # 正規化，當某間餐廳和這n間餐廳都很相似時，分數就會接近1。
        scores[k] += v / DEFAULT_RECENT_RESTAURANT_NUM * WEIGHT_R2R

    print("figure out r2r ", datetime.now())
    # 計算使用者與餐廳相似度
    restaurants_num = conn.getRestaurantsNum()
    tfidf = conn.getTFIDFWithID(uid)
    matches = {}
    from r2u import calc_r2u
    for restaurant in restaurants_num:
        matches[restaurant['rid']] = calc_r2u(user, restaurant, tfidf[restaurant['rid']])

    for r, s in matches.items():
        scores[r] += s * WEIGHT_R2U
    conn.close()

    print("figure out r2u ", datetime.now())
    recommendations = []

    import operator
    sorted_scores = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True)[:10])  # 依照分數排序前十名餐廳。

    for restaurant in restaurants:
        if restaurant['rid'] in sorted_scores:
            recommendations.append(restaurant)

    # Alter column name.
    for restaurant in recommendations:
        restaurant['tags'].extend(restaurant['remark'])
        restaurant['tags'].extend(restaurant['special'])
        restaurant['restaurant_id'] = restaurant['rid']

    js = json.dumps(recommendations, ensure_ascii=False)

    resp = Response(js, status=200, mimetype='application/json')

    return resp


def findSimilarUserRecent(uid, n=3, m=5):
    restaurants = {}
    db = DBConn()
    db.open()
    sim = db.getU2USimilarities(uid, n)
    for u, s in sim.items():
        recent = db.getUserActivity(u, m)
        for r in recent:
            if r in restaurants:
                restaurants[r] += s
            else:
                restaurants[r] = s

    for k, v in restaurants.items():
        # 正規化，所有相似使用者最近都去過某間餐廳的時候，分數就會接近1。
        restaurants[k] = v / n
    db.close()
    return restaurants


if __name__ == '__main__':
    application.debug = True
    application.run()
