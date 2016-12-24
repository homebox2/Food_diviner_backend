# -*- coding: utf-8 -*-

class db_weight():
    # 新增權重 dict:{R2R, U2R, U2U, context, ...}
    def insertWeightWithID(self, user_id, dict):
        # SQL query
        self.cursor.execute('INSERT INTO weight(user_id, ' + ', '.join(dict.keys()) + ') VALUES(%s, ' + ', '.join(['%s'] * len(dict)) + ')',
                            ((user_id,) + tuple(dict.values())))


    # 傳回使用者最新的權重
    def getWeightWithID(self, user_id):
        # SQL query
        self.cursor.execute('SELECT * from weight WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1', user_id)
        record = self.cursor.fetchall()[0]
        return {'user_id': record[1], 'R2R': record[2], 'U2R': record[3], 'U2U': record[4], 'context': record[5],
                'R2R_distance': record[6], 'R2R_price': record[7], 'R2R_ordering': record[8], 'R2R_cuisine': record[9],
                'U2R_TFIDF': record[10], 'U2R_price': record[11], 'U2R_ordering': record[12], 'U2R_cuisine': record[13],
                'U2U_tag': record[14], 'U2U_price': record[15], 'U2U_ordering': record[16], 'U2U_cuisine': record[17],
                'context_1': record[18], 'context_2': record[19], 'context_3': record[20], 'context_4': record[21]}
