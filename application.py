# -*- coding: utf8 -*-
import sys, os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime
from flask import request, abort, send_from_directory
from pymysql import IntegrityError
from werkzeug.contrib.cache import SimpleCache

from db import DBConn
from errorhandler import *

DEFAULT_RECENT_RESTAURANT_NUM = 3
DEFAULT_SIM_USER_NUM = 3
DEFAULT_SIM_USER_RESTAURANT_NUM = 5
application = Flask(__name__)

conn = DBConn()
cache = SimpleCache()

@application.route("/")
def welcome_message():
    mes = json.dumps({"message":"Hello! welcome to food_diviner API server."},indent=4)
    return Response(mes, status=200, mimetype='application/json')

@application.route("/users/<user_id>/recommendation",methods=["POST"])
def get_recommendation(user_id):
    req = request.get_json()

    conn.open()
    user = conn.getUserInfoWithID(user_id)

    if req["advance"]:
        missing = check_missing(req, ['advance', 'prefer_prices', 'weather', 'transport', 'lat', 'lng'])
        if missing:
            js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
            resp = Response(js, status=400, mimetype='application/json')
            return resp

        user["price"] = req["prefer_prices"]  # advance 啟動時覆蓋掉原本user的price
        conn.insertUserAdvanceWithID(user_id, req["prefer_prices"], req["weather"],
                                     req["transport"], req["lat"], req["lng"])

    WEIGHT_CONTEXT = 0.25
    restaurants = {r['restaurant_id']: r for r in conn.getRestaurantsInfo()}  # 將餐廳陣列轉換為以restaurant_id為key的dict。
    print("get request ", datetime.now())

    scores = {}
    for restaurant_id in restaurants.keys():
        scores[restaurant_id] = 0  # 初始化每個餐廳的分數。

    weights = conn.getWeightWithID(user_id)
    u2r_weights = {
        'price': weights['U2R_price'],
        'ordering': weights['U2R_ordering'],
        'cuisine': weights['U2R_cuisine'],
        'tfidf': weights['U2R_TFIDF']
    }

    print("init restaurant scores ", datetime.now())

    similar_users = conn.getU2USimilarities(user_id, DEFAULT_SIM_USER_NUM)
    if similar_users != -1: # 排除只有一個user情況
        u2u_sim = {}
        for u, s in similar_users.items():  # 使用者間的相似度
            user_recent = conn.getUserActivityAcceptWithID(u, DEFAULT_SIM_USER_RESTAURANT_NUM)  # 相近的使用者最近去過的餐廳。
            for r in user_recent:
                if r in u2u_sim:
                    u2u_sim[r] += s
                else:
                    u2u_sim[r] = s
        for r, s in u2u_sim.items():
            # 正規化餐廳分數並乘以u2u的權重。
            scores[r] += s / DEFAULT_SIM_USER_NUM * weights['U2U']

    print("figure out u2u ", datetime.now())
    # 找出和使用者最近去過的餐廳相似的餐廳。
    recent_restaurants = conn.getUserActivityAcceptWithID(user_id, DEFAULT_RECENT_RESTAURANT_NUM)
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
    from Algorithm_Module.u2r import calc_u2r
    for restaurant in restaurants_num:
        # TODO 把user各項count做
        matches[restaurant['restaurant_id']] = calc_u2r(user, restaurant, tfidf[restaurant['restaurant_id']], u2r_weights)

    for r, s in matches.items():
        scores[r] += s * weights['U2R']
    conn.close()

    print("figure out r2u ", datetime.now())
    recommendations = []

    import operator
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)  # 依照分數排序前十名餐廳。
    print("sorted", sorted_scores)

    # 將在推薦名單中的餐廳資訊放入list。
    counter = 0
    for restaurant_id, score in sorted_scores:
        key = str(user_id) + "-" + str(restaurant_id)
        dummy = cache.get(key)  # 利用暫存來紀錄最近被接受或拒絕過的結果，避免重複推薦。
        if not dummy:
            recommendations.append(restaurants[restaurant_id])
            counter += 1
            if counter >= 10:
                break

    # Alter column name.
    for restaurant in recommendations:
        restaurant['tags'].extend(restaurant['remark'])
        restaurant['tags'].extend(restaurant['special'])
        del restaurant['remark']
        del restaurant['special']
        # 增加 image 資料
        restaurant["image"] = [str(restaurant['restaurant_id'])]
        # import glob
        # image_list = glob.glob("./images/" + str(restaurant["restaurant_id"]) + "/*.*")
        # restaurant["image"] = [str(restaurant['restaurant_id']) + "_" + x[-6:-4] for x in image_list]

    js = json.dumps(recommendations, ensure_ascii=False, indent=4)

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
    req = request.get_json()

    # NOTE: 暫時不檢查rating
    missing = check_missing(req, ['restaurant_id', "tags"])
    if missing:
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        return resp

    conn.open()

    for k, v in req['tags'].items():
        conn.insertTagWithID(user_id, req['restaurant_id'], k, v)

    conn.close()
    return Response(status=200)

@application.route('/user_choose', methods=['POST'])
def post_choice():
    req = request.get_json()
    missing = check_missing(req, ['user_id', 'restaurant_id', 'decision', 'run'])
    if missing:
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        return resp
    if req['decision'] != 'accept' and req['decision'] != 'decline':
        js = json.dumps({'message': 'Invalid decision: %s' % req['decision']})
        resp = Response(js, status=400, mimetype='application/json')
        return resp

    if req['run'] <= 0:
        js = json.dumps({'message': 'Invalid run: %d' % req['run']})
        resp = Response(js, status=400, mimetype='application/json')
        return resp
    conn.open()
    conn.insertUserActivity(req['user_id'], req['restaurant_id'], req['run'], 1 if req['decision'] == 'accept' else -1)

    user_avg = conn.getUserAverage()
    user_ratio = conn.getUserRatio(req['user_id'])  # 取得使用者在價格、菜式、點菜方式各項屬性接受的比例。
    user_model = {}

    n = conn.getUserActivityCountWithID(req['user_id'])
    w = 0.4 - (n - 5) / 5 * 0.1 if n < 45 else 0

    for name, values in user_ratio.items():
        model = []
        avg_values = user_avg[name]
        for idx, value in enumerate(values):
            """為避免前期使用者接受過的餐廳數量不足而出現極端值，在前期將平均值乘以較高的權重來平衡這個數值。"""
            model.append(value * w + avg_values[idx] * (1 - w))
        user_model[name] = model

    conn.insertUserModelWithID(req['user_id'], user_model['price'], user_model['ordering'], user_model['cuisine'])

    key = str(req['user_id']) + "-" + str(req['restaurant_id'])
    if req['decision'] == 'accept':  # 將使用者接受的餐廳1天不推薦
        cache.set(key, "recommended", 86400)
    else:  # 拒絕的餐廳三天不推薦
        cache.set(key, "recommended", 345600)
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
    missing = check_missing(req, ['user_key', 'user_trial', 'name', 'gender'])
    if missing:  # 如果缺少欄位，回傳400錯誤。
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        return resp
    if req['gender'] != 'M' and req['gender'] != 'F':
        js = json.dumps({'message': 'Invalid gender: %s' % req['gender']})
        resp = Response(js, status=400, mimetype='application/json')
        return resp
    conn.open()
    init_weight = {
        'R2R': 0.25,
        'U2R': 0.25,
        'U2U': 0.25,
        'context': 0.25,
        'R2R_cuisine': 0.35,
        'R2R_ordering': 0.15,
        'R2R_price': 0.3,
        'R2R_distance': 0.2,
        'context_1': 0.25,
        'context_2': 0.25,
        'context_3': 0.25,
        'context_4': 0.25,
        'U2U_ordering': 0.25,
        'U2U_tag': 0.25,
        'U2U_price': 0.25,
        'U2U_cuisine': 0.25,
        'U2R_TFIDF': 0.25,
        'U2R_ordering': 0.25,
        'U2R_cuisine': 0.25,
        'U2R_price': 0.25
    }
    try:
        user_id = conn.insertUserInfo(req['name'], req['gender'], req['user_key'], '')
        conn.insertWeightWithID(user_id, init_weight)

        for restaurant_id, result in req['user_trial'].items():
            conn.insertUserActivity(user_id, eval(restaurant_id), 0, 1 if result == 1 else -1)  # 第0 run就接受或拒絕代表初始問題。

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

        users = conn.getUsersInfo()
        this_user = conn.getUserInfoWithID(user_id)
        from Algorithm_Module.u2u import calc_u2u

        u2u_weight = {
            "tag": init_weight['U2U_tag'],
            "price": init_weight['U2U_price'],
            "cuisine": init_weight['U2U_cuisine'],
            "ordering": init_weight['U2U_ordering']
        }
        u2u_similarities = []
        for user in users:
            u2u_similarities.append((user['user_id'], user_id, float(calc_u2u(this_user, user, u2u_weight))))
        print("update u2u", u2u_similarities)
        conn.updateU2USimilarities(u2u_similarities)
        js = json.dumps({'user_id': user_id}, ensure_ascii=False)

        return Response(js, status=200, mimetype='application/json')
    except IntegrityError:
        js = json.dumps({'message': 'This User_key %s has been registered' % req['user_key']})
        resp = Response(js, status=409, mimetype='application/json')
        return resp
    finally:
        conn.close()

@application.route('/test', methods=['POST'])
def test_fb_registered():
    req = request.get_json()
    missing = check_missing(req, ['user_key'])
    if missing:  # 如果缺少欄位，回傳400錯誤。
        js = json.dumps({'message': 'Missing field(s): ' + ', '.join(missing)})
        resp = Response(js, status=400, mimetype='application/json')
        return resp
    conn.open()
    user_id = conn.getUserIDWithUserKey(req['user_key'])
    conn.close()
    if not user_id:
        js = json.dumps({'message': 'This account is not registered'})
        resp = Response(js, status=404, mimetype='application/json')
        return resp
    else:
        js = json.dumps({'user_id': user_id}, ensure_ascii=False)
        return Response(js, status=200, mimetype='application/json')

@application.route('/images/<image_id>')
def get_image(image_id):
    image_name = "{0:03}".format(int(image_id)) + ".jpg"
    dir_path = './images/'

    try:
        return send_from_directory(dir_path, image_name)
    except:
        js = json.dumps({'message': 'picture not found!'})
        return Response(js, status=405, mimetype='application/json')

@application.route('/users/<user_id>/caches', methods=['DELETE'])
def invalidate(user_id):
    conn.open()
    for r in conn.getRestaurantsNum():
        cache.delete("-".join([user_id, str(r['restaurant_id'])]))
    conn.close()
    js = json.dumps({'success': True})
    return Response(js, status=200, mimetype='application/json')

@application.route('/users/<user_id>/delete', methods=['DELETE'])
def deleteUser(user_id):
    conn.open()
    mes = conn.deleteUserInfo(user_id)
    js = json.dumps({"message":mes})
    return Response(js,status=200,mimetype='application/json')

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
    application.debug = True
    application.run()
