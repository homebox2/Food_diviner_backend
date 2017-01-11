"""
計算餐廳之間的相似度。
"""

from Algorithm_Module.similarity import similarity

# WEIGHT_DISTANCE = 0.2
# WEIGHT_PRICE = 0.3
# WEIGHT_ORDERING = 0.15
# WEIGHT_CUISINE = 0.35


def calc_r2r(r1, r2, distance, order_sim_matrix, cuisine_sim_matrix, weight):
    """
    計算兩間餐廳的相似度
    :param r1 餐廳物件 。
    :param r2 餐廳物件。
    :param distance 兩間餐廳的距離。
    :param order_sim_matrix 點菜方式的相似矩陣。
    :param cuisine_sim_matrix 餐廳菜式的相似矩陣。
    :return: 餐廳之間的相似度，介於0~1之間。數值越大代表相似度越高。 
    """
    distance_sim = calc_distance_sim(distance) * weight["distance"]
    price_sim = calc_price_sim(r1["price"], r2["price"]) * weight["price"]
    ordering_sim = calc_ordering_sim(r1["ordering"], r2["ordering"], order_sim_matrix) * weight["ordering"]
    cuisine_sim = calc_cuisine_sim(r1["cuisine"], r2["cuisine"], cuisine_sim_matrix) * weight["cuisine"]
    return distance_sim + price_sim + ordering_sim + cuisine_sim


def calc_distance_sim(distance):
    """
    由兩間餐廳的距離來計算餐廳之間的相似度。
    :param distance: 兩間餐廳的距離，單位為公里。
    :return:
    """
    if distance < 0:
        return 0
    sim = (1 - distance ** 2)
    return sim if sim > 0 else 0


# Price similarity
def calc_price_sim(price1, price2):
    return similarity(price1, price2)


# Ordering similarity
def calc_ordering_sim(ordering1, ordering2, matrix):
    return similarity(ordering1, ordering2, matrix)


# Cuisine similarity
def calc_cuisine_sim(cuisine1, cuisine2, matrix):
    return similarity(cuisine1, cuisine2, matrix)


if __name__ == '__main__':
    # 直接執行r2R.py的時候，輸出餐廳相似矩陣的csv
    from db import DBConn

    weight = {"distance":0.2,"price":0.3,"ordering":0.15,"cuisine":0.35}

    conn = DBConn()
    conn.open()
    restaurants_num = conn.getRestaurantsNum()
    order_sim＿matrix = conn.getOrderingSimMatrix()
    cuisine_sim_matrix = conn.getCuisineSimMatrix()
    num = len(restaurants_num)
    similarities = []
    for i, restaurant1 in enumerate(restaurants_num):
        for j in range(i, num):
            restaurant2 = restaurants_num[j]

            sim = calc_r2r(restaurant1, restaurant2, conn.getRestaurantDistance(restaurant1['restaurant_id'], restaurant2['restaurant_id']),
                           order_sim＿matrix, cuisine_sim_matrix,weight) if restaurant1['restaurant_id'] != restaurant2['restaurant_id'] else 1
            similarities.append((restaurant1['restaurant_id'], restaurant2['restaurant_id'], sim))
            print(restaurant1)
            print(restaurant2)
            print(sim)

    conn.close()

    print(similarities)