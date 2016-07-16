import json
import logging
from datetime import datetime

from flask import Flask, request, Response, abort

from db import DBConn

DEFAULT_RECENT_RESTAURANT_NUM = 3
DEFAULT_SIM_USER_NUM = 3
DEFAULT_SIM_USER_RESTAURANT_NUM = 5
application = Flask(__name__)

conn = DBConn()


@application.route("/users/<user_id>/recommendation")
def get_recommendation(user_id):
    conn.open()

    weights = conn.getWeightWithID(user_id)
    r2u_weights = {
        'price': weights['U2R_price'],
        'ordering': weights['U2R_ordering'],
        'cuisine': weights['U2R_cuisine'],
        'tfidf': weights['U2R_TFIDF']
    }

    WEIGHT_CONTEXT = 0.25

    conn.open()
    user = conn.getUserInfoWithID(user_id)
    restaurants = conn.getRestaurantsInfo()
    print("get request ", datetime.now())
    scores = {}
    for restaurant in restaurants:
        scores[restaurant['rid']] = 0  # 初始化每個餐廳的分數。
    print("init restaurant scores ", datetime.now())
    similar_users = conn.getU2USimilarities(user_id, DEFAULT_SIM_USER_NUM)
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
        scores[r] += s / DEFAULT_SIM_USER_NUM * weights['U2U']

    print("figure out u2u ", datetime.now())
    # 找出和使用者最近去過的餐廳相似的餐廳。
    recent_restaurants = conn.getUserActivity(user_id, DEFAULT_RECENT_RESTAURANT_NUM)
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
        scores[k] += v / DEFAULT_RECENT_RESTAURANT_NUM * weights['R2R']

    print("figure out r2r ", datetime.now())
    # 計算使用者與餐廳相似度
    restaurants_num = conn.getRestaurantsNum()
    tfidf = conn.getTFIDFWithID(user_id)

    matches = {}
    from r2u import calc_r2u
    for restaurant in restaurants_num:
        matches[restaurant['rid']] = calc_r2u(user, restaurant, tfidf[restaurant['rid']], r2u_weights)

    for r, s in matches.items():
        scores[r] += s * weights['U2R']
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


@application.route('/users/<user_id>/collections', methods=['POST', 'GET'])
def collect_restaurant(user_id):
    if request.method == 'GET':
        collection_ids = conn.getUserCollection(user_id)
        collections = conn.getRestaurantInfoWithIDs(collection_ids)
        js = json.dumps(collections, ensure_ascii=False)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    req = request.get_json()
    missing = check_missing(req, ['restaurant_id', 'run'])
    if missing:
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        return resp

    conn.open()
    conn.insertUserActivity(user_id, req['restaurant_id'], req['run'], 0)
    conn.close()
    return Response(status=200)


@application.route('/users/<user_id>/ratings', methods=['POST'])
def post_user_ratings(user_id):
    abort(501)


@application.route('/user_choose', methods=['POST'])
def post_choice():
    req = request.get_json()
    missing = check_missing(req, ['user_id', 'restaurant_id', 'decision', 'run'])
    if missing:
        req = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(req, status=400, mimetype='application/json')
        return resp
    if req['decision'] != 'accept' or req['decision'] != 'decline':
        req = json.dumps({'message': 'Invalid decision: %s' % req['decision']})
        resp = Response(req, status=400, mimetype='application/json')
        return resp

    if req['run'] <= 0:
        req = json.dumps({'message': 'Invalid run: %d' % req['run']})
        resp = Response(req, status=400, mimetype='application/json')
        return resp
    conn.open()
    conn.insertUserActivity(req['user_id'], req['restaurant_id'], req['run'], 1 if req['decision'] == 'accept' else -1)

    user_avg = conn.getUserAverage()
    user_ratio = conn.getUserRatio(req['user_id'])  # 取得使用者在價格、菜式、點菜方式各項屬性接受的比例。
    user_model = {}

    n = 0  # TODO: 依照目前使用者做過的決定來計算w
    w = 0.4 - (n - 5) / 5 * 0.1 if n < 45 else 0

    for name, values in user_ratio.items():
        model = []
        avg_values = user_avg[name]
        for idx, value in enumerate(values):
            """為避免前期使用者接受過的餐廳數量不足而出現極端值，在前期將平均值乘以較高的權重來平衡這個數值。"""
            model.append(value * w + avg_values[idx] * (1 - w))
        user_model[name] = model

    conn.insertUserModelWithID(req['user_id'], user_model['price'], user_model['ordering'], user_model['cuisine'])

    conn.close()
    return Response(status=200)


@application.route('/restaurants/<restaurant_id>/ratings')
def get_restaurant_ratings(restaurant_id):
    """
    取得指定餐廳的評價及tag。
    :param restaurant_id: 指定餐廳的id。
    :return: 平均評價及各tag的數量。
    """
    abort(501)


@application.route('/signup', methods=['POST'])
def register():
    """
    提交用戶的id以及初始試驗的五家餐廳的喜好，以建立使用者Model。
    """

    req = request.get_json()
    missing = check_missing(req, ['fb_id', 'user_trial', 'name', 'gender'])
    if missing:  # 如果缺少欄位，回傳400錯誤。
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        logging.debug("400: " + str(req))
        return resp
    if req['gender'] != 'M' and req['gender'] != 'F':
        js = json.dumps({'message': 'Invalid gender: %s' % req['gender']})
        resp = Response(js, status=400, mimetype='application/json')
        logging.debug("400: " + str(req))
        return resp
    conn.open()
    user_id = conn.insertUserInfo(req['name'], req['gender'], req['fb_id'], '')
    conn.insertWeightWithID(user_id,
                            {'R2R_cuisine': 0.265, 'context_3': 0.292, 'R2R_ordering': 0.288, 'U2U_ordering': 0.322,
                             'U2U_tag': 0.235, 'context_2': 0.25, 'R2R_price': 0.187, 'R2R': 0.344, 'context_1': 0.173,
                             'U2R_TFIDF': 0.173, 'R2R_distance': 0.26, 'U2U_cuisine': 0.159, 'U2U': 0.292,
                             'U2U_price': 0.284, 'U2R_ordering': 0.214, 'context_4': 0.285, 'U2R': 0.3,
                             'U2R_cuisine': 0.369, 'context': 0.064, 'U2R_price': 0.244}

                            )

    for rid, result in req['user_trial'].items():
        conn.insertUserActivity(user_id, eval(rid), 0, 1 if result else -1)  # 第0 run就接受或拒絕代表初始問題。

    user_avg = conn.getUserAverage()
    user_ratio = conn.getUserRatio(user_id)  # 取得使用者在價格、菜式、點菜方式各項屬性接受的比例。
    user_model = {}
    w = 0.4
    for name, values in user_ratio.items():
        model = []
        avg_values = user_avg[name]
        for idx, value in enumerate(values):
            """為避免前期使用者接受過的餐廳數量不足而出現極端值，在前期將平均值乘以較高的權重來平衡這個數值。"""
            model.append(value * w + avg_values[idx] * (1 - w))
        user_model[name] = model

    conn.insertUserModelWithID(user_id, user_model['price'], user_model['ordering'], user_model['cuisine'])
    conn.close()
    js = json.dumps({'user_id': user_id}, ensure_ascii=False)

    return Response(js, status=200, mimetype='application/json')


@application.route('/test', methods=['POST'])
def test_fb_registered():
    req = request.get_json()
    missing = check_missing(req, ['fb_id'])
    if missing:  # 如果缺少欄位，回傳400錯誤。
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        logging.debug("400: " + str(req))
        return resp
    conn.open()
    user_id = conn.getUserIdWithAccount(req['fb_id'])
    conn.close()
    if not user_id:
        js = json.dumps({'message': 'FB account is not registered'})
        resp = Response(js, status=404, mimetype='application/json')
        logging.debug("404: " + str(req))
        return resp
    else:
        js = json.dumps({'user_id': user_id}, ensure_ascii=False)
        return Response(js, status=200, mimetype='application/json')


@application.errorhandler(405)
def handle_405(error):
    js = json.dumps({'message': 'Method not allowed'})
    resp = Response(js, status=405, mimetype='application/json')
    return resp


@application.errorhandler(404)
def handle_404(error):
    js = json.dumps({'message': 'Method not defined'})
    resp = Response(js, status=404, mimetype='application/json')
    logging.debug("404: " + str(request.get_json()))
    return resp


@application.errorhandler(501)
def handle_501(error):
    resp = Response(json.dumps({'message': 'Method not implemented'}), status=501, mimetype='application/json')
    logging.debug("501: " + str(request.get_json()))
    return resp


@application.errorhandler(500)
def handle_500(error):
    resp = Response(json.dumps({'message': 'Unknown error'}), status=500, mimetype='application/json')
    logging.debug("500: " + str(request.get_json()))
    return resp


def check_missing(actual, expect_fields):
    """
    檢查收到的請求欄位是否完整。
    :param actual: 實際收到得請求Dict。
    :param expect_fields: 需要的欄位名稱List。
    :return: 缺少的欄位名稱List。
    """
    missing = []
    for field in expect_fields:
        if field not in actual:
            missing.append(field)
    return missing


if __name__ == '__main__':
    logging.basicConfig(filename='error.log', level=logging.DEBUG)

    application.debug = True
    application.run()
