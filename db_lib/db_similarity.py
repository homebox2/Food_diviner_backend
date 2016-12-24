# -*- coding: utf-8 -*-
from numpy import mat

class db_similarity():
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
    def updateR2RSimilarity(self, restaurant_id1, restaurant_id2, value):
        # DB的儲存方式為restaurant_id1 < restaurant_id2
        if restaurant_id1 > restaurant_id2:
            restaurant_id1, restaurant_id2 = restaurant_id2, restaurant_id1

        # SQL query
        self.cursor.execute('INSERT INTO R2RSimilarity(restaurant_id1, restaurant_id2, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (restaurant_id1, restaurant_id2, value, value))


    # 新增/更新多筆R2R的相似度 list:[(restaurant_id1, restaurant_id2, sim), ...] restaurant_id1 < restaurant_id2
    def updateR2RSimilarities(self, list):
        param = [((x[1], x[0]) if x[0] > x[1] else (x[0], x[1])) + (x[2], x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO R2RSimilarity(restaurant_id1, restaurant_id2, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)


    # 傳回兩間餐廳的相似度
    def getR2RSimilarity(self, restaurant_id1, restaurant_id2):
        # DB的儲存方式為restaurant_id1 < restaurant_id2
        if restaurant_id1 > restaurant_id2:
            restaurant_id1, restaurant_id2 = restaurant_id2, restaurant_id1

        # SQL query
        self.cursor.execute('SELECT similarity FROM R2RSimilarity WHERE restaurant_id1 = %s AND restaurant_id2 = %s', (restaurant_id1, restaurant_id2))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]


    # 傳回餐廳對所有餐廳的相似度
    def getR2RSimilarities(self, restaurant_id, same=False):
        # SQL query
        if same:
            # 包含restaurant_id
            self.cursor.execute('SELECT restaurant_id2, similarity FROM R2RSimilarity WHERE restaurant_id1 = %s UNION '
                                'SELECT restaurant_id1, similarity FROM R2RSimilarity WHERE restaurant_id2 = %s '
                                'ORDER BY restaurant_id2', (restaurant_id, restaurant_id))
        else:
            # 不包含restaurant_id
            self.cursor.execute('SELECT restaurant_id2, similarity FROM R2RSimilarity WHERE restaurant_id1 = %s AND restaurant_id2 != %s UNION '
                                'SELECT restaurant_id1, similarity FROM R2RSimilarity WHERE restaurant_id2 = %s AND restaurant_id1 != %s '
                                'ORDER BY restaurant_id2', (restaurant_id, restaurant_id, restaurant_id, restaurant_id))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}


    # 新增/更新U2R的相似度
    def updateU2RSimilarity(self, user_id, restaurant_id, value):
        # SQL query
        self.cursor.execute('INSERT INTO U2RSimilarity(user_id, restaurant_id, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (user_id, restaurant_id, value, value))


    # 新增/更新多筆U2R的相似度 list:[(user_id, restaurant_id, sim), ...]
    def updateU2RSimilarities(self, list):
        param = [x + (x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO U2RSimilarity(user_id, restaurant_id, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)


    # 傳回使用者對餐廳的相似度
    def getU2RSimilarity(self, user_id, restaurant_id):
        # SQL query
        self.cursor.execute('SELECT similarity FROM U2RSimilarity WHERE user_id = %s AND restaurant_id = %s', (user_id, restaurant_id))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]


    # 傳回使用者對所有餐廳的相似度
    def getU2RSimilarities(self, user_id):
        # SQL query
        self.cursor.execute('SELECT similarity FROM U2RSimilarity WHERE user_id = %s ORDER BY restaurant_id', user_id)

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}


    # 新增/更新U2U的相似度
    def updateU2USimilarity(self, user_id1, user_id2, value):
        # DB的儲存方式為user_id1 < user_id2
        if user_id1 > user_id2:
            user_id1, user_id2 = user_id2, user_id1

        # SQL query
        self.cursor.execute('INSERT INTO U2USimilarity(user_id1, user_id2, similarity) VALUES(%s, %s, %s) '
                            'ON DUPLICATE KEY UPDATE similarity = %s', (user_id1, user_id2, value, value))


    # 新增/更新多筆U2U的相似度 list:[(user_id1, user_id2, sim), ...] user_id1 < user_id2
    def updateU2USimilarities(self, list):
        param = [((x[1], x[0]) if x[0] > x[1] else (x[0], x[1])) + (x[2], x[2],) for x in list]

        # SQL query
        self.cursor.executemany('INSERT INTO U2USimilarity(user_id1, user_id2, similarity) VALUES(%s, %s, %s) '
                                'ON DUPLICATE KEY UPDATE similarity = %s', param)


    # 傳回兩個使用者的相似度
    def getU2USimilarity(self, user_id1, user_id2):
        # DB的儲存方式為user_id1 < user_id2
        if user_id1 > user_id2:
            user_id1, user_id2 = user_id2, user_id1

        # SQL query
        self.cursor.execute('SELECT similarity FROM U2USimilarity WHERE user_id1 = %s AND user_id2 = %s', (user_id1, user_id2))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]


    # 傳回使用者對所有使用者的相似度
    def getU2USimilarities(self, user_id, n, same=False):
        # SQL query
        if same:
            # 包含user_id
            self.cursor.execute('SELECT user_id2, similarity FROM U2USimilarity WHERE user_id1 = %s UNION '
                                'SELECT user_id1, similarity FROM U2USimilarity WHERE user_id2 = %s '
                                'ORDER BY similarity DESC LIMIT %s', (user_id, user_id, n))
        else:
            # 不包含user_id
            self.cursor.execute('SELECT user_id2, similarity FROM U2USimilarity WHERE user_id1 = %s AND user_id2 != %s UNION '
                                'SELECT user_id1, similarity FROM U2USimilarity WHERE user_id2 = %s AND user_id1 != %s '
                                'ORDER BY similarity DESC LIMIT %s', (user_id, user_id, user_id, user_id, n))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return -1

        return {key: value for (key, value) in self.cursor.fetchall()}


    # 傳回使用者對餐廳的TFIDF
    def getTFIDFWithIDs(self, user_id, restaurant_id):
        # SQL query
        self.cursor.execute('SELECT SUM(TFIDF) FROM (SELECT (COUNT(*) / (SELECT COUNT(*) FROM tags WHERE restaurant_id = %s) * IDF) AS TFIDF '
                            'FROM ((SELECT tag, LOG((SELECT COUNT(*) FROM restaurantInfo) / COUNT(DISTINCT restaurant_id)) AS IDF FROM tags GROUP BY tag) AS A '
                            'NATURAL JOIN (SELECT tag FROM tags WHERE user_id = %s GROUP BY tag) AS B '
                            'NATURAL JOIN (SELECT tag FROM tags WHERE restaurant_id = %s) AS C) GROUP BY tag) AS D', (restaurant_id, user_id, restaurant_id))

        # DB回傳的結果為空
        if self.cursor.rowcount == 0:
            return 0

        return self.cursor.fetchall()[0][0]


    # 傳回使用者對所有餐廳的TFIDF
    def getTFIDFWithID(self, user_id):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, IFNULL(SUM(TFIDF), 0) FROM (SELECT restaurant_id, ((COUNT(*) / TOTAL) * IDF) AS TFIDF FROM '
                            '(SELECT restaurant_id FROM restaurantInfo) AS A LEFT JOIN '
                            '((SELECT restaurant_id, tag FROM tags) AS B NATURAL JOIN '
                            '(SELECT tag, LOG((SELECT COUNT(*) FROM restaurantInfo) / COUNT(DISTINCT restaurant_id)) AS IDF FROM tags GROUP BY tag) AS C NATURAL JOIN '
                            '(SELECT tag FROM tags WHERE user_id = %s GROUP BY tag) AS D) USING(restaurant_id) LEFT JOIN '
                            '(SELECT restaurant_id, COUNT(*) AS TOTAL FROM tags GROUP BY restaurant_id) AS E USING(restaurant_id) '
                            'GROUP BY restaurant_id, tag) AS F GROUP BY(restaurant_id)', user_id)

        return {key: float(value) for (key, value) in self.cursor.fetchall()}
