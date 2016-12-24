# -*- coding: utf-8 -*-
from ast import literal_eval

class db_user():
    # 新增使用者的基本資訊
    def insertUserInfo(self, name, gender, user_key, password):
        # SQL query
        self.cursor.execute('INSERT INTO userInfo(name, gender, user_key, password) '
                            'SELECT %s, %s, %s, %s FROM DUAL WHERE NOT EXISTS '
                            '(SELECT * FROM userInfo WHERE user_key = %s)', (name, gender, user_key, password, user_key))

        user_id = self.cursor.lastrowid

        if user_id == 0:
            return -1  # already exists
        else:
            # 初始化userPrice, userOrdering, userCuisine
            self.cursor.execute('INSERT INTO userPrice(user_id, price_id, has) VALUES' + ', '.join(['(%s, ' + str(id) + ', 0)' for id in range(1, 6)]) + ';'
                                                                                                                                                         'INSERT INTO userOrdering(user_id, ordering_id, has) VALUES' + ', '.join(
                ['(%s, ' + str(id) + ', 0)' for id in range(1, 6)]) + ';'
                                                                      'INSERT INTO userCuisine(user_id, cuisine_id, has) VALUES' + ', '.join(['(%s, ' + str(id) + ', 0)' for id in range(1, 11)]) + ';',
                                ((user_id,) * 20))
            # 回傳他的 user_id
            return user_id


    # 傳回所有使用者的資訊
    def getUsersInfo(self):
        # SQL query price ordering cuisine
        self.cursor.execute("SELECT user_id, name, gender, user_key, password, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id) FROM userPrice P WHERE P.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id) FROM userOrdering O WHERE O.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id) FROM userCuisine C WHERE C.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.user_id = I.user_id) "
                            "FROM userInfo I ORDER BY user_id")
        result = self.cursor.fetchall()

        # 宣告空list
        lists = []

        for record in result:
            price = list(literal_eval(record[5]))

            ordering = list(literal_eval(record[6]))

            cuisine = list(literal_eval(record[7]))

            tags = [x for x in record[8].split(',')] if record[8] is not None else []

            # 每筆資料用dict存
            dict = {'user_id': record[0], 'name': record[1], 'gender': record[2], 'user_key': record[3], 'password': record[4],
                    'price': price, 'ordering': ordering, 'cuisine': cuisine, 'tags': tags}

            # 把每筆資料存到list
            lists.append(dict)

        return lists


    # 傳回使用者的基本資訊
    def getUserInfoWithID(self, user_id):
        # SQL query price ordering cuisine
        self.cursor.execute("SELECT user_id, name, gender, user_key, password, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id) FROM userPrice P WHERE P.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id) FROM userOrdering O WHERE O.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id) FROM userCuisine C WHERE C.user_id = I.user_id), "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.user_id = I.user_id) "
                            "FROM userInfo I WHERE user_id = %s", user_id)

        # DB回傳的結果為空(user_id錯誤)
        if self.cursor.rowcount == 0:
            return []

        record = self.cursor.fetchall()[0]

        price = list(literal_eval(record[5]))

        ordering = list(literal_eval(record[6]))

        cuisine = list(literal_eval(record[7]))

        tags = [x for x in record[8].split(',')] if record[8] is not None else []

        # 每筆資料用dict存
        dict = {'user_id': record[0], 'name': record[1], 'gender': record[2], 'user_key': record[3], 'password': record[4],
                'price': price, 'ordering': ordering, 'cuisine': cuisine, 'tags': tags}

        return dict


    # 刪除使用者的基本資訊
    def deleteUserInfo(self, user_id):
        # SQL query
        self.cursor.execute("DELETE FROM userInfo WHERE user_id = %s", user_id)

        return "delete UserInfo success!"


    # 傳回使用者的帳號
    def getUserKeyWithID(self, user_id):
        # SQL query
        self.cursor.execute('SELECT user_key FROM userInfo WHERE user_id = %s', user_id)

        return self.cursor.fetchall()[0][0]


    # 傳回使用者的ID
    def getUserIDWithUserKey(self, user_key):
        # SQL query
        self.cursor.execute('SELECT user_id FROM userInfo WHERE user_key = %s', user_key)

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return None

        return self.cursor.fetchall()[0][0]


    # 修改使用者的price屬性
    def updateUserPriceWithID(self, user_id, price_id, value):
        # SQL query
        self.cursor.execute('UPDATE userPrice SET has = has + %s WHERE user_id = %s AND price_id = %s', (value, user_id, price_id))


    # 修改使用者的ordering屬性
    def updateUserOrderingWithID(self, user_id, ordering_id, value):
        # SQL query
        self.cursor.execute('UPDATE userOrdering SET has = has + %s WHERE user_id = %s AND ordering_id = %s', (value, user_id, ordering_id))


    # 修改使用者的cuisine屬性
    def updateUserCuisineWithID(self, user_id, cuisine_id, value):
        # SQL query
        self.cursor.execute('UPDATE userCuisine SET has = has + %s WHERE user_id = %s AND cuisine_id = %s', (value, user_id, cuisine_id))


    # 新增使用者的活動(run:第幾次 result:接受(1)、收藏(0)、拒絕(-1))
    def insertUserActivity(self, user_id, restaurant_id, run, result):
        # 接受 price ordering cuisine增加
        if result == 1:
            self.cursor.execute('INSERT INTO userActivity(user_id, restaurant_id, run, result) VALUES(%s, %s, %s, %s);'
                                'UPDATE userPrice AS A INNER JOIN restaurantPrice AS B USING(price_id) '
                                'SET A.has = A.has + B.has WHERE user_id = %s AND restaurant_id = %s;'
                                'UPDATE userOrdering AS A INNER JOIN restaurantOrdering AS B USING(ordering_id) '
                                'SET A.has = A.has + B.has WHERE user_id = %s AND restaurant_id = %s;'
                                'UPDATE userCuisine AS A INNER JOIN restaurantCuisine AS B USING(cuisine_id) '
                                'SET A.has = A.has + B.has WHERE user_id = %s AND restaurant_id = %s;',
                                (user_id, restaurant_id, run, result, user_id, restaurant_id, user_id, restaurant_id, user_id, restaurant_id))
        # 收藏
        elif result == 0:
            self.cursor.execute('INSERT INTO userActivity(user_id, restaurant_id, run, result) VALUES(%s, %s, %s, %s);'
                                'INSERT INTO userCollection(user_id, restaurant_id) VALUES(%s, %s) '
                                'ON DUPLICATE KEY UPDATE timestamp = NOW()', (user_id, restaurant_id, run, result, user_id, restaurant_id))
        # 拒絕
        elif result == -1:
            self.cursor.execute('INSERT INTO userActivity(user_id, restaurant_id, run, result) VALUES(%s, %s, %s, %s)', (user_id, restaurant_id, run, result))


    # 傳回使用者最後n個接受的餐廳
    def getUserActivityAcceptWithID(self, user_id, n):
        # SQL query
        self.cursor.execute('SELECT restaurant_id FROM userActivity WHERE user_id = %s AND result = 1 ORDER BY timestamp DESC LIMIT %s', (user_id, n))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return []

        return [x[0] for x in self.cursor.fetchall()]


    # 傳回使用者接受和拒絕的餐廳數量
    def getUserActivityCountWithID(self, user_id):
        # SQL query
        self.cursor.execute('SELECT COUNT(*) FROM userActivity WHERE user_id = %s AND (result = 1 OR result = -1)', (user_id))

        return self.cursor.fetchall()[0][0]


    # 新增/更新使用者的各項分數
    def insertUserModelWithID(self, user_id, price, ordering, cuisine):
        priceStr = str(price)
        orderingStr = str(ordering)
        cuisineStr = str(cuisine)

        # SQL query
        self.cursor.execute('INSERT INTO userModel(user_id, priceScore, orderingScore, cuisineScore) VALUES(%s, %s, %s, %s)',
                            (user_id, priceStr, orderingStr, cuisineStr))


    # 傳回使用者最新的各項分數
    def getUserModelWithID(self, user_id):
        # SQL query
        self.cursor.execute('SELECT user_id, priceScore, orderingScore, cuisineScore FROM userModel WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', user_id)

        record = self.cursor.fetchall()[0]

        price = literal_eval(record[1])

        ordering = literal_eval(record[2])

        cuisine = literal_eval(record[3])

        # 每筆資料用dict存
        dict = {'user_id': record[0], 'priceScore': price, 'orderingScore': ordering, 'cuisineScore': cuisine}

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


    # 新增使用者收藏
    def insertUserCollection(self, user_id, restaurant_id):
        self.cursor.execute('INSERT INTO userCollection(user_id, restaurant_id) VALUES(%s, %s) '
                            'ON DUPLICATE KEY UPDATE timestamp = NOW()', (user_id, restaurant_id))


    # 傳回使用者收藏的餐廳
    def getUserCollection(self, user_id):
        # SQL query
        self.cursor.execute('SELECT restaurant_id FROM userCollection WHERE user_id = %s', user_id)

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return []

        return [x[0] for x in self.cursor.fetchall()]


    # 刪除收藏
    def deleteUserCollection(self, user_id, restaurant_id):
        # SQL query
        self.cursor.execute('DELETE FROM userCollection WHERE user_id = %s AND restaurant_id = %s', (user_id, restaurant_id))


    def getUserRatio(self, user_id):
        # SQL query
        self.cursor.execute('SELECT * FROM (SELECT GROUP_CONCAT(IFNULL(ACC / TOTAL, 0) ORDER BY price_id) FROM (SELECT price_id, SUM(has) AS ACC FROM '
                            '(SELECT * FROM userActivity WHERE result = 1) AS A '
                            'NATURAL JOIN (SELECT * FROM restaurantPrice) AS B WHERE user_id = %s GROUP BY price_id) AS C '
                            'NATURAL JOIN (SELECT price_id, SUM(has) AS TOTAL FROM (SELECT * FROM userActivity WHERE result = 1 OR result = -1) AS D '
                            'NATURAL JOIN (SELECT * FROM restaurantPrice) AS E WHERE user_id = %s GROUP BY price_id) AS F) AS G, '
                            '(SELECT GROUP_CONCAT(IFNULL(ACC / TOTAL, 0) ORDER BY ordering_id) FROM (SELECT ordering_id, SUM(has) AS ACC FROM '
                            '(SELECT * FROM userActivity WHERE result = 1) AS A '
                            'NATURAL JOIN (SELECT * FROM restaurantOrdering) AS B WHERE user_id = %s GROUP BY ordering_id) AS C '
                            'NATURAL JOIN (SELECT ordering_id, SUM(has) AS TOTAL FROM (SELECT * FROM userActivity WHERE result = 1 OR result = -1) AS D '
                            'NATURAL JOIN (SELECT * FROM restaurantOrdering) AS E WHERE user_id = %s GROUP BY ordering_id) AS F) AS H, '
                            '(SELECT GROUP_CONCAT(IFNULL(ACC / TOTAL, 0) ORDER BY cuisine_id) FROM (SELECT cuisine_id, SUM(has) AS ACC FROM '
                            '(SELECT * FROM userActivity WHERE result = 1) AS A '
                            'NATURAL JOIN (SELECT * FROM restaurantCuisine) AS B WHERE user_id = %s GROUP BY cuisine_id) AS C '
                            'NATURAL JOIN (SELECT cuisine_id, SUM(has) AS TOTAL FROM (SELECT * FROM userActivity WHERE result = 1 OR result = -1) AS D '
                            'NATURAL JOIN (SELECT * FROM restaurantCuisine) AS E WHERE user_id = %s GROUP BY cuisine_id) AS F) AS I',
                            (user_id, user_id, user_id, user_id, user_id, user_id))

        record = self.cursor.fetchall()[0]

        # 該使用者沒資料
        if record[0] is None:
            return {'price': [0.0 for i in range(5)], 'ordering': [0.0 for i in range(5)], 'cuisine': [0.0 for i in range(10)]}

        return {'price': list(literal_eval(record[0])), 'ordering': list(literal_eval(record[1])), 'cuisine': list(literal_eval(record[2]))}


    # 新增使用者的進階搜尋
    def insertUserAdvanceWithID(self, user_id, price, weather, transport, lat, lng):
        price = str(price)

        # SQL query
        self.cursor.execute('INSERT INTO userAdvance(user_id, prefer_price, weather, transport, lat, lng) VALUES(%s, %s, %s, %s, %s, %s)',
                            (user_id, price, weather, transport, lat, lng))


    # 傳回使用者最近n次的進階搜尋
    def getUserAdvanceWithID(self, user_id, n):
        # SQL query
        self.cursor.execute('SELECT * FROM userAdvance WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s', (user_id, n))

        result = self.cursor.fetchall()

        # 宣告空list
        lists = []

        for record in result:
            # 每筆資料用dict存
            dict = {'user_id': record[1], 'price': list(literal_eval(record[2])), 'weather': record[3], 'transport': record[4],
                    'lat': record[5], 'lng': record[6]}

            lists.append(dict)

        return lists