# -*- coding: utf-8 -*-
from ast import literal_eval

class db_restaurant:
    # 傳回餐廳全部的資料
    def getRestaurantsAll(self):
        # SQL query
        self.cursor.execute("SELECT restaurant_id, name, address, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id) FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id) FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id) FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "scenario, special, phone, hours1, remark, "
                            "(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) FROM restaurantInfo I ORDER BY restaurant_id")
        result = self.cursor.fetchall()

        # 宣告空list
        lists = []

        for record in result:
            # ┌───────────────┬──────┬─────────┬─────────┬──────────┬─────────┬──────────┬─────────┬───────┬────────┬────────┐
            # │ restaurant_id │ name │ address │ price   │ ordering │ cuisine │ scenario │ special │ phone │ hours  │ remark │
            # │ 編號           │ 店名　│ 地址　　　│ 均價區間　│ 點菜方式　 │ 菜式　　　│ 用餐情境　 │ 招牌菜　　│ 電話　 │ 營業時間 │ 備註　  │
            # └───────────────┴──────┴─────────┴─────────┴──────────┴─────────┴──────────┴─────────┴───────┴────────┴────────┘
            # 字串格式為unicode
            # 電話、營業時間有可能為空值(NULL), DB會回傳None

            # [0~100, 100~200, 200~300, 300~500, 500~]
            price = list(literal_eval(record[3]))

            # [單點, 吃到飽, 套餐, 合菜, 簡餐]
            ordering = list(literal_eval(record[4]))

            # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
            cuisine = list(literal_eval(record[5]))

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
            dict = {'restaurant_id': record[0], 'name': record[1], 'address': record[2], 'price': price, 'ordering': ordering, 'cuisine': cuisine,
                    'scenario': scenario, 'special': special, 'phone': record[8], 'hours': hours, 'remark': remark, 'tags': tags}

            # 把每筆資料存到list
            lists.append(dict)

        # 回傳
        return lists


    # 傳回餐廳的數值化資料: ID, 價格, 點菜方式, 菜式, 營業時間
    def getRestaurantsNum(self):
        # SQL query
        self.cursor.execute("SELECT restaurant_id, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id) FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id) FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id) FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "hours1, (SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) "
                            "FROM restaurantInfo I ORDER BY restaurant_id")
        result = self.cursor.fetchall()

        # 宣告空list
        lists = []

        for record in result:
            # [0~100, 100~200, 200~300, 300~500, 500~]
            price = list(literal_eval(record[1]))

            # [單點, 吃到飽, 套餐, 合菜, 簡餐]
            ordering = list(literal_eval(record[2]))

            # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
            cuisine = list(literal_eval(record[3]))

            # {星期幾: ['開門時間~關門時間', ...], ...}
            hours = literal_eval(record[4]) if record[4] is not None else None

            # ['tag', ...]
            tags = [x for x in record[5].split(',')] if record[5] is not None else []

            # 每筆資料用dict存
            dict = {'restaurant_id': record[0], 'price': price, 'ordering': ordering, 'cuisine': cuisine, 'hours': hours, 'tags': tags}

            # 把每筆資料存到list
            lists.append(dict)

        # 回傳
        return lists


    # 傳回指定餐廳的數值化資料: 價格, 點菜方式, 菜式, 營業時間
    def getRestaurantNumWithID(self, restaurant_id):
        # SQL query
        self.cursor.execute("SELECT restaurant_id, "
                            "(SELECT GROUP_CONCAT(has ORDER BY price_id) FROM restaurantPrice P WHERE P.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY ordering_id) FROM restaurantOrdering O WHERE O.restaurant_id = I.restaurant_id), "
                            "(SELECT GROUP_CONCAT(has ORDER BY cuisine_id) FROM restaurantCuisine C WHERE C.restaurant_id = I.restaurant_id), "
                            "hours1, (SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) "
                            "FROM restaurantInfo I WHERE restaurant_id = %s", restaurant_id)

        # DB回傳的結果為空(restaurant_id錯誤)
        if self.cursor.rowcount == 0:
            return []

        record = self.cursor.fetchall()[0]

        # [0~100, 100~200, 200~300, 300~500, 500~]
        price = list(literal_eval(record[1]))

        # [單點, 吃到飽, 套餐, 合菜, 簡餐]
        ordering = list(literal_eval(record[2]))

        # [中式料理, 日式料理, 韓式料理, 泰式料理, 異國料理, 燒烤, 鍋類, 小吃, 便當, 冰品、甜點、下午茶]
        cuisine = list(literal_eval(record[3]))

        # {星期幾: ['開門時間~關門時間', ...], ...}
        hours = literal_eval(record[4]) if record[4] is not None else None

        # ['tag', ...]
        tags = [x for x in record[5].split(',')] if record[5] is not None else []

        # 每筆資料用dict存
        dict = {'restaurant_id': record[0], 'price': price, 'ordering': ordering, 'cuisine': cuisine, 'hours': hours, 'tags': tags}

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
            dict = {'restaurant_id': record[0], 'name': record[1], 'address': record[2], 'price': record[3], 'ordering': ordering, 'cuisine': cuisine,
                    'scenario': scenario, 'special': special, 'phone': record[8], 'hours': record[9], 'remark': remark, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        # 回傳
        return list


    # 傳回多間餐廳的文字資訊 list:[restaurant_id1, restaurant_id2, ...]
    def getRestaurantInfoWithIDs(self, list):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, name, address, price, ordering, cuisine, scenario, special, phone, hours, remark, '
                            '(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) '
                            'FROM restaurantInfo I WHERE restaurant_id IN (' + ', '.join('%s' for x in range(len(list))) + ') ORDER BY restaurant_id', list)
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
            dict = {'restaurant_id': record[0], 'name': record[1], 'address': record[2], 'price': record[3], 'ordering': ordering, 'cuisine': cuisine,
                    'scenario': scenario, 'special': special, 'phone': record[8], 'hours': record[9], 'remark': remark, 'tags': tags}

            # 把每筆資料存到list
            list.append(dict)

        # 回傳
        return list


    # 傳回餐廳的文字資訊
    def getRestaurantInfoWithID(self, restaurant_id):
        # SQL query
        self.cursor.execute('SELECT restaurant_id, name, address, price, ordering, cuisine, scenario, special, phone, hours, remark, '
                            '(SELECT GROUP_CONCAT(DISTINCT tag) FROM tags T WHERE T.restaurant_id = I.restaurant_id) '
                            'FROM restaurantInfo I WHERE restaurant_id = %s', restaurant_id)

        # DB回傳的結果為空(restaurant_id錯誤)
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
        dict = {'restaurant_id': record[0], 'name': record[1], 'address': record[2], 'price': record[3], 'ordering': ordering, 'cuisine': cuisine,
                'scenario': scenario, 'special': special, 'phone': record[8], 'hours': record[9], 'remark': remark, 'tags': tags}

        return dict


    # 傳回兩間餐廳的距離
    def getRestaurantDistance(self, restaurant_id1, restaurant_id2):
        # 同一間餐廳的距離為1
        if restaurant_id1 == restaurant_id2:
            return 1

        # DB的儲存方式為restaurant_id1 < restaurant_id2
        if restaurant_id1 > restaurant_id2:
            restaurant_id1, restaurant_id2 = restaurant_id2, restaurant_id1

        # SQL query
        self.cursor.execute('SELECT distance FROM restaurantDistance WHERE restaurant_id1 = %s AND restaurant_id2 = %s', (restaurant_id1, restaurant_id2))

        # DB回傳的結果為空(restaurant_id錯誤)
        if self.cursor.rowcount == 0:
            return -1

        return self.cursor.fetchall()[0][0]
