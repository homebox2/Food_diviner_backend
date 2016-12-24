# -*- coding: utf-8 -*-

class db_tag():
    # 新增tag(type: 1喜歡 -1討厭)
    def insertTagWithID(self, user_id, restaurant_id, tag, type):
        self.cursor.execute('INSERT INTO tags(user_id, restaurant_id, tag, type) VALUES(%s, %s, %s, %s)', (user_id, restaurant_id, tag, type))


    # 新增多筆tag list:[(user_id, restaurant_id, tag, type), ...]
    def insertTagsWithID(self, list):
        self.cursor.executemany('INSERT INTO tags(user_id, restaurant_id, tag, type) VALUES(%s, %s, %s, %s)', list)


    # 傳回某間餐廳的個別tag數量
    def getRestaurantTagCount(self, restaurant_id):
        # SQL query
        self.cursor.execute('SELECT tag, COUNT(*) FROM tags WHERE restaurant_id = %s GROUP BY tag', restaurant_id)
        return dict(self.cursor.fetchall())


    # 傳回有這個tag的餐廳restaurant_id
    def getRestaurantWithTag(self, tag):
        # SQL query
        self.cursor.execute('SELECT DISTINCT restaurant_id FROM tags WHERE tag = %s', tag)
        return [x[0] for x in self.cursor.fetchall()]


    # 傳回這個tag的總數量
    def getTagCount(self, tag):
        # SQL query
        self.cursor.execute('SELECT COUNT(*) FROM tags WHERE tag = %s', tag)
        return self.cursor.fetchall()[0][0]
