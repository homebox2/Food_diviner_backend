# -*- coding: utf-8 -*-
import pymysql
from numpy import mat
from ast import literal_eval

class DBConn:

    # 建構式
    def __init__(self):

        self.host = '52.78.68.151'
        self.user = 'dbm'
        self.passwd = '5j0 wu654yji4'
        self.dbname = 'warofdata'
        '''
        self.host = 'stevie.heliohost.org'
        self.user = 'datawar_user1'
        self.passwd = '[QzJUoHwFtq0'
        self.dbname = 'datawar_warofdata1'
        '''

    # 建立連線
    def open(self):
        self.db = pymysql.connect(self.host, self.user, self.passwd, self.dbname, charset='utf8')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()
        self.cursor.execute("SET TIME_ZONE = '+08:00'")

    # 關閉連線
    def close(self):
        self.cursor.close()
        self.db.close()

    # ========== RESTAURANT ==========
    # 傳回餐廳全部的資料
    def getRestaurantsAll(self):
        #SQL query
        self.cursor.execute("SELECT restaurant_id, name, address, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id SEPARATOR '') FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id SEPARATOR '') FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id SEPARATOR '') FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "scenario, special, phone, hours2, remark, "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) FROM restaurantInfo I ORDER BY restaurant_id")
        result = self.cursor.fetchall()

        # 宣告空list
        list = []

        for record in result:
            # ┌─────┬──────┬─────────┬─────────┬──────────┬─────────┬──────────┬─────────┬───────┬────────┬────────┐
            # │ rid │ name │ address │ price   │ ordering │ cuisine │ scenario │ special │ phone │ hours  │ remark │
            # │ 編號 │ 店名　│ 地址　　　│ 均價區間　│ 點菜方式　 │ 菜式　　　│ 用餐情境　 │ 招牌菜　　│ 電話　 │ 營業時間 │ 備註　  │
            # └─────┴──────┴─────────┴─────────┴──────────┴─────────┴──────────┴─────────┴───────┴────────┴────────┘
            # 字串格式為unicode
            # 電話、營業時間有可能為空值(NULL), DB會回傳None

            # [0~100, 100~200, 200~300, 300~500, 500~]
            price = [int(x) for x in record[3]]

            # [單點, 吃到飽, 套餐, 合菜, 簡餐]
            ordering = [int(x) for x in record[4]]

            # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
            cuisine = [int(x) for x in record[5]]

            # ['用餐情境', ...]
            scenario = literal_eval(record[6])

            # ['招牌菜', ...]
            special = literal_eval(record[7])

            # {星期幾: ['開門時間~關門時間', ...], ...}
            hours = literal_eval(record[9]) if record[9] is not None else None

            # ['備註', ...]
            remark = literal_eval(record[10])

            # ['tag', ...]
            tags = [x for x in record[11].split(',')] if record[11] is not None else []

            # 每筆資料用dict存
            dict = {'rid': record[0], 'name': record[1], 'address': record[2], 'price': price, 'ordering': ordering, 'cuisine': cuisine,
                    'scenario': scenario, 'special': special, 'phone': record[8], 'hours': hours, 'remark': remark, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        # 回傳
        return list

    # 傳回餐廳的數值化資料: ID, 價格, 點菜方式, 菜式, 營業時間
    def getRestaurantsNum(self):
        # SQL query
        self.cursor.execute("SELECT restaurant_id, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id SEPARATOR '') FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id SEPARATOR '') FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id SEPARATOR '') FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "hours2, (SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) "
                            "FROM restaurantInfo I ORDER BY restaurant_id")
        result = self.cursor.fetchall()

        # 宣告空list
        list = []

        for record in result:

            # [0~100, 100~200, 200~300, 300~500, 500~]
            price = [int(x) for x in record[1]]

            # [單點, 吃到飽, 套餐, 合菜, 簡餐]
            ordering = [int(x) for x in record[2]]

            # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
            cuisine = [int(x) for x in record[3]]

            # {星期幾: ['開門時間~關門時間', ...], ...}
            hours = literal_eval(record[4]) if record[4] is not None else None

            # ['tag', ...]
            tags = [x for x in record[5].split(',')] if record[5] is not None else []

            # 每筆資料用dict存
            dict = {'rid': record[0], 'price': price, 'ordering': ordering, 'cuisine': cuisine, 'hours': hours, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        # 回傳
        return list

    # 傳回指定餐廳的數值化資料: 價格, 點菜方式, 菜式, 營業時間
    def getRestaurantNumWithID(self, rid):
        # SQL query
        self.cursor.execute("SELECT restaurant_id, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id SEPARATOR '') FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id SEPARATOR '') FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id SEPARATOR '') FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "hours2, (SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) "
                            "FROM restaurantInfo I WHERE restaurant_id = %s", rid)

        # DB回傳的結果為空(rid錯誤)
        if self.cursor.rowcount == 0:
            return []

        record = self.cursor.fetchall()[0]

        # [0~100, 100~200, 200~300, 300~500, 500~]
        price = [int(x) for x in record[1]]

        # [單點, 吃到飽, 套餐, 合菜, 簡餐]
        ordering = [int(x) for x in record[2]]

        # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
        cuisine = [int(x) for x in record[3]]

        # {星期幾: ['開門時間~關門時間', ...], ...}
        hours = literal_eval(record[4]) if record[4] is not None else None

        # ['tag', ...]
        tags = [x for x in record[5].split(',')] if record[5] is not None else []

        # 每筆資料用dict存
        dict = {'rid': record[0], 'price': price, 'ordering': ordering, 'cuisine': cuisine, 'hours': hours, 'tags': tags}

        return dict

    # 傳回餐廳的文字資訊
    def getRestaurantsInfo(self):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, name, address, price, ordering, cuisine, scenario, special, phone, hours, remark, '
                            '(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) FROM restaurantInfo I ORDER BY restaurant_id')
        result = self.cursor.fetchall()

        # 宣告空list
        list = []

        for record in result:

            # ['點菜方式', ...]
            ordering = literal_eval(record[4])

            # ['菜式', ...]
            cuisine = literal_eval(record[5])

            # ['用餐情境', ...]
            scenario = literal_eval(record[6])

            # ['招牌菜', ...]
            special = literal_eval(record[7])

            # ['備註', ...]
            remark = literal_eval(record[10])

            # ['tag', ...]
            tags = [x for x in record[11].split(',')] if record[11] is not None else []

            # 每筆資料用dict存
            dict = {'rid': record[0], 'name': record[1], 'address': record[2], 'price': record[3], 'ordering': ordering, 'cuisine': cuisine,
                    'scenario': scenario, 'special': special, 'phone': record[8], 'hours': record[9], 'remark': remark, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        # 回傳
        return list

    # 傳回餐廳的文字資訊
    def getRestaurantInfoWithID(self, rid):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, name, address, price, ordering, cuisine, scenario, special, phone, hours, remark, '
                            '(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) '
                            'FROM restaurantInfo I WHERE restaurant_id = %s', rid)

        # DB回傳的結果為空(rid錯誤)
        if self.cursor.rowcount == 0:
            return []

        record = self.cursor.fetchall()[0]

        # ['點菜方式', ...]
        ordering = literal_eval(record[4])

        # ['菜式', ...]
        cuisine = literal_eval(record[5])

        # ['用餐情境', ...]
        scenario = literal_eval(record[6])

        # ['招牌菜', ...]
        special = literal_eval(record[7])

        # ['備註', ...]
        remark = literal_eval(record[10])

        # ['tag', ...]
        tags = [x for x in record[11].split(',')] if record[11] is not None else []

        # 每筆資料用dict存
        dict = {'rid': record[0], 'name': record[1], 'address': record[2], 'price': record[3], 'ordering': ordering, 'cuisine': cuisine,
                'scenario': scenario, 'special': special, 'phone': record[8], 'hours': record[9], 'remark': remark, 'tags': tags}

        return dict

    # 傳回兩間餐廳的距離
    def getRestaurantDistance(self, rid1, rid2):
        # 同一間餐廳的距離為1
        if rid1 == rid2:
            return 1

        # DB的儲存方式為rid1 < rid2
        if rid1 > rid2:
            rid1, rid2 = rid2, rid1

        # SQL query
        self.cursor.execute('SELECT distance FROM restaurantDistance WHERE restaurant_id1 = %s AND restaurant_id2 = %s', (rid1, rid2))

        # DB回傳的結果為空(rid錯誤)
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]


    # ========== USER ==========
    # 新增使用者的基本資訊
    def insertUserInfo(self, name, gender, account):
        # SQL query
        self.cursor.execute('INSERT INTO userInfo(name, gender, account) VALUES(%s, %s, %s)', (name, gender, account))

        # TODO price cuisine ordering的值?

        # 回傳他的uid
        return self.cursor.lastrowid

    # 傳回所有使用者的資訊
    def getUsersInfo(self):
        # SQL query price ordering cuisine
        self.cursor.execute("SELECT user_id, name, gender, account, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id SEPARATOR '') FROM userPrice P WHERE P.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id SEPARATOR '') FROM userOrdering O WHERE O.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id SEPARATOR '') FROM userCuisine C WHERE C.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.user_id = I.user_id) "
                            "FROM userInfo I ORDER BY user_id")
        result = self.cursor.fetchall()

        # 宣告空list
        list = []

        for record in result:

            price = [int(x) for x in record[4]]

            ordering = [int(x) for x in record[5]]

            cuisine = [int(x) for x in record[6]]

            tags = [x for x in record[7].split(',')] if record[7] is not None else []

            # 每筆資料用dict存
            dict = {'uid': record[0], 'name': record[1], 'gender': record[2], 'account': record[3], 'price': price,
                    'ordering': ordering, 'cuisine': cuisine, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        return list

    # 傳回使用者的基本資訊
    def getUserInfoWithID(self, uid):
        # SQL query price ordering cuisine
        self.cursor.execute("SELECT user_id, name, gender, account, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id SEPARATOR '') FROM userPrice P WHERE P.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id SEPARATOR '') FROM userOrdering O WHERE O.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id SEPARATOR '') FROM userCuisine C WHERE C.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.user_id = I.user_id) "
                            "FROM userInfo I WHERE user_id = %s", uid)

        # DB回傳的結果為空(rid錯誤)
        if self.cursor.rowcount == 0:
            return []

        record = self.cursor.fetchall()[0]

        price = [int(x) for x in record[4]]

        ordering = [int(x) for x in record[5]]

        cuisine = [int(x) for x in record[6]]

        tags = [x for x in record[7].split(',')] if record[7] is not None else []

        # 每筆資料用dict存
        dict = {'uid': record[0], 'name': record[1], 'gender': record[2], 'account': record[3], 'price': price,
                'ordering': ordering, 'cuisine': cuisine, 'tags': tags}

        return dict

    # 修改使用者的price屬性
    def updateUserPriceWithID(self, uid, price_id, value):
        # SQL query
        self.cursor.execute('UPDATE userPrice SET has = has + %s WHERE user_id = %s AND price_id = %s', (value, uid, price_id))

    # 修改使用者的ordering屬性
    def updateUserOrderingWithID(self, uid, ordering_id, value):
        # SQL query
        self.cursor.execute('UPDATE userOrdering SET has = has + %s WHERE user_id = %s AND ordering_id = %s', (value, uid, ordering_id))

    # 修改使用者的cuisine屬性
    def updateUserCuisineWithID(self, uid, cuisine_id, value):
        # SQL query
        self.cursor.execute('UPDATE userCuisine SET has = has + %s WHERE user_id = %s AND cuisine_id = %s', (value, uid, cuisine_id))

    # 新增使用者的活動(run:第幾次 result:接受(1)、收藏(0)、拒絕(-1))
    def insertUserActivity(self, uid, rid, run, result):
        # SQL query
        self.cursor.execute('INSERT INTO userActivity(user_id, restaurant_id, run, result) VALUES(%s, $s, %s, %s)', (uid, rid, run, result))

    # 傳回使用者最後n個接受的餐廳
    def getUserActivity(self, uid, n):
        # SQL query
        self.cursor.execute('SELECT restaurant_id FROM userActivity WHERE user_id = %s AND result = 1 ORDER BY timestamp DESC LIMIT %s', (uid, n))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return []

        return [x[0] for x in self.cursor.fetchall()]

    # 新增/更新使用者的各項分數
    def updateUserModel(self, uid, price, ordering, cuisine):

        priceStr = str(price)
        orderingStr = str(ordering)
        cuisineStr = str(cuisine)

        # SQL query
        self.cursor.execute('INSERT INTO userModel(user_id, priceScore, orderingScore, cuisineScore) VALUES(%s, %s, %s, %s) ON DUPLICATE KEY '
                            'UPDATE priceScore = %s, orderingScore = %s, cuisineScore = %s', (uid, priceStr, orderingStr, cuisineStr, priceStr, orderingStr, cuisineStr))

    # 傳回使用者的各項分數
    def getUserModel(self, uid):
        # SQL query
        self.cursor.execute('SELECT * FROM userModel WHERE user_id = %s', uid)

        record = self.cursor.fetchall()[0]

        price = literal_eval(record[1])

        ordering = literal_eval(record[2])

        cuisine = literal_eval(record[3])

        # 每筆資料用dict存
        dict = {'uid': record[0], 'price': price, 'ordering': ordering, 'cuisine': cuisine}

        return dict

    # 傳回預設的使用者起始值
    def getUserAverage(self):
        # SQL query
        self.cursor.execute('SELECT * FROM userAverage')

        record = self.cursor.fetchall()[0]

        price = literal_eval(record[1])

        cuisine = literal_eval(record[2])

        ordering = literal_eval(record[3])

        # 每筆資料用dict存
        dict = {'price': price, 'cuisine': cuisine, 'ordering': ordering, 'weatherPrio': record[4], 'distancePrio': record[5],
                'pricePrio': record[6], 'cuisinePrio': record[7], 'soupPrio': record[8], 'ratePrio': record[9]}

        return dict


    # ========== TAG ==========
    # 新增tag(type: 1喜歡 -1討厭)
    def insertTagWithID(self, uid, rid, tag, type):
        self.cursor.execute('INSERT INTO tags(user_id, restaurant_id, tag, type) VALUES(%s, %s, %s, %s)', (uid, rid, tag, type))

    # 新增多筆tag list:[(uid, rid, tag, type), ...]
    def insertTagsWithID(self, list):
        self.cursor.executemany('INSERT INTO tags(user_id, restaurant_id, tag, type) VALUES(%s, %s, %s, %s)', list)

    # 傳回某間餐廳的個別tag數量
    def getRestaurantTagCount(self, rid):
        # SQL query
        self.cursor.execute('SELECT tag, COUNT(*) FROM tags WHERE restaurant_id = %s GROUP BY tag', rid)
        return dict(self.cursor.fetchall())

    # 傳回有這個tag的餐廳rid
    def getRestaurantWithTag(self, tag):
        # SQL query
        self.cursor.execute('SELECT DISTINCT restaurant_id FROM tags WHERE tag = %s', tag)
        return [x[0] for x in self.cursor.fetchall()]

    # 傳回這個tag的總數量
    def getTagCount(self, tag):
        # SQL query
        self.cursor.execute('SELECT COUNT(*) FROM tags WHERE tag = %s', tag)
        return self.cursor.fetchall()[0][0]


    # ========== SIMILARITY ==========
    # 傳回ordering的相似矩陣
    def getOrderingSimMatrix(self):
        # 矩陣初始化
        matrix = [[0.0 if i != j else 1.0 for i in range(5)] for j in range(5)]

        # SQL query
        self.cursor.execute('SELECT * FROM orderingSimilarity')
        result = self.cursor.fetchall()

        for record in result:
            matrix[record[0] - 1][record[1] - 1] = record[2]
            matrix[record[1] - 1][record[0] - 1] = record[2]

        return mat(matrix)

    # 傳回cuisine的相似矩陣
    def getCuisineSimMatrix(self):
        # 矩陣初始化
        matrix = [[0.0 if i != j else 1.0 for i in range(10)] for j in range(10)]

        # SQL query
        self.cursor.execute('SELECT * FROM cuisineSimilarity')
        result = self.cursor.fetchall()

        for record in result:
            matrix[record[0] - 1][record[1] - 1] = record[2]
            matrix[record[1] - 1][record[0] - 1] = record[2]

        return mat(matrix)

    # 新增/更新R2R的相似度
    def updateR2RSimilarity(self, rid1, rid2, value):
        # DB的儲存方式為rid1 < rid2
        if rid1 > rid2:
            rid1, rid2 = rid2, rid1

        # SQL query
        self.cursor.execute('INSERT INTO R2RSimilarity(restaurant_id1, restaurant_id2, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (rid1, rid2, value, value))

    # 新增/更新多筆R2R的相似度 list:[(rid1, rid2, sim), ...] rid1 < rid2
    def updateR2RSimilarities(self, list):
        param = [x + (x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO R2RSimilarity(restaurant_id1, restaurant_id2, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)

    # 傳回兩間餐廳的相似度
    def getR2RSimilarity(self, rid1, rid2):
        # DB的儲存方式為rid1 < rid2
        if rid1 > rid2:
            rid1, rid2 = rid2, rid1

        # SQL query
        self.cursor.execute('SELECT similarity FROM R2RSimilarity WHERE restaurant_id1 = %s AND restaurant_id2 = %s', (rid1, rid2))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]

    # 傳回餐廳對所有餐廳的相似度
    def getR2RSimilarities(self, rid, same=False):
        # SQL query
        if same:
            # 包含rid
            self.cursor.execute('SELECT restaurant_id2, similarity FROM R2RSimilarity WHERE restaurant_id1 = %s UNION '
                                'SELECT restaurant_id1, similarity FROM R2RSimilarity WHERE restaurant_id2 = %s '
                                'ORDER BY restaurant_id2', (rid, rid))
        else:
            # 不包含rid
            self.cursor.execute('SELECT restaurant_id2, similarity FROM R2RSimilarity WHERE restaurant_id1 = %s AND restaurant_id2 != %s UNION '
                                'SELECT restaurant_id1, similarity FROM R2RSimilarity WHERE restaurant_id2 = %s AND restaurant_id1 != %s '
                                'ORDER BY restaurant_id2', (rid, rid, rid, rid))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}

    # 新增/更新U2R的相似度
    def updateU2RSimilarity(self, uid, rid, value):
        # SQL query
        self.cursor.execute('INSERT INTO U2RSimilarity(user_id, restaurant_id, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (uid, rid, value, value))

    # 新增/更新多筆U2R的相似度 list:[(uid, rid, sim), ...]
    def updateU2RSimilarities(self, list):
        param = [x + (x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO U2RSimilarity(user_id, restaurant_id, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)

    # 傳回使用者對餐廳的相似度
    def getU2RSimilarity(self, uid, rid):
        # SQL query
        self.cursor.execute('SELECT similarity FROM U2RSimilarity WHERE user_id = %s AND restaurant_id = %s', (uid, rid))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]

    # 傳回使用者對所有餐廳的相似度
    def getU2RSimilarities(self, uid):
        # SQL query
        self.cursor.execute('SELECT similarity FROM U2RSimilarity WHERE user_id = %s ORDER BY restaurant_id', uid)

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}

    # 新增/更新U2U的相似度
    def updateU2USimilarity(self, uid1, uid2, value):
        # DB的儲存方式為uid1 < uid2
        if uid1 > uid2:
            rid1, rid2 = uid2, uid1

        # SQL query
        self.cursor.execute('INSERT INTO U2USimilarity(user_id1, user_id2, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (uid1, uid2, value, value))

    # 新增/更新多筆U2U的相似度 list:[(uid1, uid2, sim), ...] uid1 < uid2
    def updateU2USimilarities(self, list):
        param = [x + (x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO U2USimilarity(user_id1, user_id2, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)

    # 傳回兩個使用者的相似度
    def getU2USimilarity(self, uid1, uid2):
        # DB的儲存方式為uid1 < uid2
        if uid1 > uid2:
            uid1, uid2 = uid2, uid1

        # SQL query
        self.cursor.execute('SELECT similarity FROM U2USimilarity WHERE user_id1 = %s AND user_id2 = %s', (uid1, uid2))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]

    # 傳回使用者對所有使用者的相似度
    def getU2USimilarities(self, uid, n, same=False):
        # SQL query
        if same:
            # 包含uid
            self.cursor.execute('SELECT user_id2, similarity FROM U2USimilarity WHERE user_id1 = %s UNION '
                                'SELECT user_id1, similarity FROM U2USimilarity WHERE user_id2 = %s '
                                'ORDER BY similarity DESC LIMIT %s', (uid, uid, n))
        else:
            # 不包含uid
            self.cursor.execute('SELECT user_id2, similarity FROM U2USimilarity WHERE user_id1 = %s AND user_id2 != %s UNION '
                                'SELECT user_id1, similarity FROM U2USimilarity WHERE user_id2 = %s AND user_id1 != %s '
                                'ORDER BY similarity DESC LIMIT %s', (uid, uid, uid, uid, n))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}

    # 傳回使用者對餐廳的TFIDF
    def getTFIDFWithIDs(self, uid, rid):
        # SQL query
        self.cursor.execute('SELECT SUM(TFIDF) FROM (SELECT (COUNT(*) / (SELECT COUNT(*) FROM tags WHERE restaurant_id = %s) * IDF) AS TFIDF '
                            'FROM ((SELECT tag, LOG((SELECT COUNT(*) FROM restaurantInfo) / COUNT(DISTINCT restaurant_id)) AS IDF FROM tags GROUP BY tag) AS A '
                            'NATURAL JOIN (SELECT tag FROM tags WHERE user_id = %s GROUP BY tag) AS B '
                            'NATURAL JOIN (SELECT tag FROM tags WHERE restaurant_id = %s) AS C) GROUP BY tag) AS D', (rid, uid, rid))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return 0

        return self.cursor.fetchall()[0][0]

    # 傳回使用者對所有餐廳的TFIDF
    def getTFIDFWithID(self, uid):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, IFNULL(SUM(TFIDF), 0) FROM (SELECT restaurant_id, ((COUNT(*) / TOTAL) * IDF) AS TFIDF FROM '
                            '(SELECT restaurant_id FROM restaurantInfo) AS A LEFT JOIN '
                            '((SELECT restaurant_id, tag FROM tags) AS B NATURAL JOIN '
                            '(SELECT tag, LOG((SELECT COUNT(*) FROM restaurantInfo) / COUNT(DISTINCT restaurant_id)) AS IDF FROM tags GROUP BY tag) AS C NATURAL JOIN '
                            '(SELECT tag FROM tags WHERE user_id = %s GROUP BY tag) AS D) USING(restaurant_id) LEFT JOIN '
                            '(SELECT restaurant_id, COUNT(*) AS TOTAL FROM tags GROUP BY restaurant_id) AS E USING(restaurant_id) '
                            'GROUP BY restaurant_id, tag) AS F GROUP BY(restaurant_id)', uid)

        return {key: float(value) for (key, value) in self.cursor.fetchall()}


    # ========== WEIGHT ==========
    # 更新總體的權重
    def insertTotalWeight(self, R2R, U2R, U2U):
        # SQL query
        self.cursor.execute('INSERT INTO totalWeight(r2r, u2r, u2u) VALUES(%s, %s, %s)', (R2R, U2R, U2U))

    # 傳回總體的權重
    def getTotalWeight(self):
        # SQL query
        self.cursor.execute('SELECT r2r, u2r, u2u FROM totalWeight ORDER BY timestamp DESC LIMIT 1')
        record = self.cursor.fetchall()[0]
        return {'R2R': record[0], 'U2R': record[1], 'U2U': record[2]}

    # 更新R2R的權重
    def insertR2RWeightWithID(self, rid, distance, price, ordering, cuisine):
        # SQL query
        self.cursor.execute('INSERT INTO R2RWeight(user_id, distance, price, ordering, cuisine) VALUES(%s, %s, %s, %s, %s)', (distance, price, ordering, cuisine))

    # 傳回R2R最新的權重
    def getR2RWeightWithID(self, rid):
        # SQL query
        self.cursor.execute('SELECT distance, price, ordering, cuisine FROM R2RWeight WHERE restaurant_id = %s ORDER BY timestamp DESC LIMIT 1', rid)
        record = self.cursor.fetchall()[0]
        return {'distance': record[0], 'price': record[1], 'ordering': record[2], 'cuisine': record[3]}

    # 更新U2R的權重
    def insertU2RWeightWithID(self, uid, TFIDF, price, ordering, cuisine):
        # SQL query
        self.cursor.execute('INSERT INTO U2RWeight(user_id, tfidf, price, ordering, cuisine) VALUES(%s, %s, %s, %s, %s) ', (uid, TFIDF, price, ordering, cuisine))

    # 傳回U2R最新的權重
    def getU2RWeightWithID(self, uid):
        # SQL query
        self.cursor.execute('SELECT tfidf, price, ordering, cuisine FROM U2RWeight WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', uid)
        record = self.cursor.fetchall()[0]
        return {'tfidf': record[0], 'price': record[1], 'ordering': record[2], 'cuisine': record[3]}

    # 更新U2U的權重
    def insertU2UWeightWithID(self, uid, tag, price, ordering, cuisine):
        # SQL query
        self.cursor.execute('INSERT INTO U2UWeight(user_id, tag, price, ordering, cuisine) VALUES(%s, %s, %s, %s, %s) ', (tag, price, ordering, cuisine))

    # 傳回U2U最新的權重
    def getU2UWeightWithID(self, uid):
        # SQL query
        self.cursor.execute('SELECT tag, price, ordering, cuisine FROM U2UWeight WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', uid)
        record = self.cursor.fetchall()[0]
        return {'tag': record[0], 'price': record[1], 'ordering': record[2], 'cuisine': record[3]}

# 常用的update? => executemany
# timestamp? => which table?