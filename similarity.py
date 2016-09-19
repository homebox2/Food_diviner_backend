"""
計算各種相似度。
"""

from numpy import array
from numpy import dot
from numpy.linalg import norm


def cos(u, v):
    """
     計算兩個向量的夾角。
    """
    norm_u = norm(u)
    norm_v = norm(v)
    return dot(u, v) / (norm_u * norm_v) if norm_u != 0 and norm_v != 0 else 0


def similarity(a, b, sim_matrix=None):
    """
     計算兩個向量的相似度。
     :param a
     :param b
     :param sim_matrix 向量元素對應的相似度。
    """
    if sim_matrix is not None:
        # a = (a * sim_matrix)[:,0]
        # b = (b * sim_matrix)[:,0]

        # 拿出matrix的第一個row
        a = array(a * sim_matrix).reshape(-1, )
        b = array(b * sim_matrix).reshape(-1, )
    return cos(a, b)
