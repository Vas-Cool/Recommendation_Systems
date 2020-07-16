import os, sys

module_path = os.path.abspath(os.path.join(os.pardir))

if module_path not in sys.path:
    sys.path.append(module_path)
    
import pandas as pd
import numpy as np

# Для работы с матрицами
from scipy.sparse import csr_matrix

# Матричная факторизация
from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import ItemItemRecommender  # нужен для одного трюка
from implicit.nearest_neighbours import bm25_weight, tfidf_weight



class MainRecommender:
    """Рекоммендации, которые можно получить из ALS
    
    Input
    -----
    user_item_matrix: pd.DataFrame
        Матрица взаимодействий user-item
    """
    
    def __init__(self, data, item_features, weighting=True):
                
        # Топ покупок каждого юзера
        self.top_purchases = data.groupby(['user_id', 'item_id'])['quantity'].count().reset_index()
        self.top_purchases.sort_values('quantity', ascending=False, inplace=True)
        self.top_purchases = self.top_purchases[self.top_purchases['item_id'] != 999999]

        # Топ покупок по всему датасету
        self.overall_top_purchases = data.groupby('item_id')['quantity'].count().reset_index()
        self.overall_top_purchases.sort_values('quantity', ascending=False, inplace=True)
        self.overall_top_purchases = self.overall_top_purchases[self.overall_top_purchases['item_id'] != 999999]
        self.overall_top_purchases = self.overall_top_purchases.item_id.tolist()
        
        self.user_item_matrix = self.prepare_matrix(data)  # pd.DataFrame
        self.id_to_itemid, self.id_to_userid, self.itemid_to_id, self.userid_to_id = prepare_dicts(self.user_item_matrix)
        
        # Словарь {item_id: 0/1}. 0/1 - факт принадлежности товара к СТМ
        self.item_id_to_ctm = dict(zip(item_features['item_id'], (item_features['brand']=='Private').astype(int)))
        
        # Own recommender обучается до взвешивания матрицы
        self.own_recommender = self.fit_own_recommender(self.user_item_matrix)
        
        if weighting:
            self.user_item_matrix = bm25_weight(self.user_item_matrix.T).T 
        
        self.model = self.fit(self.user_item_matrix)
     
    @staticmethod
    def prepare_matrix(data):
        
        data= prefilter_items(data, take_n_popular=5000)
        user_item_matrix = pd.pivot_table(data_train2, 
                                  index='user_id', columns='item_id', 
                                  values='value', 
                                  aggfunc='sum', 
                                  fill_value=0
                                 )

        user_item_matrix = user_item_matrix.astype(float) # необходимый тип матрицы для implicit
        
        return user_item_matrix
    
    @staticmethod
    def prepare_dicts(user_item_matrix):
        """Подготавливает вспомогательные словари"""
        
        userids = user_item_matrix.index.values
        itemids = user_item_matrix.columns.values

        matrix_userids = np.arange(len(userids))
        matrix_itemids = np.arange(len(itemids))

        id_to_itemid = dict(zip(matrix_itemids, itemids))
        id_to_userid = dict(zip(matrix_userids, userids))

        itemid_to_id = dict(zip(itemids, matrix_itemids))
        userid_to_id = dict(zip(userids, matrix_userids))
        
        return id_to_itemid, id_to_userid, itemid_to_id, userid_to_id
     
    @staticmethod
    def fit_own_recommender(user_item_matrix):
        """Обучает модель, которая рекомендует товары, среди товаров, купленных юзером"""
    
        own_recommender = ItemItemRecommender(K=1, num_threads=4)
        own_recommender.fit(csr_matrix(user_item_matrix).T.tocsr())
        
        return own_recommender
    
    @staticmethod
    def fit(user_item_matrix, n_factors=20, regularization=0.001, iterations=15, num_threads=4):
        """Обучает ALS"""
        
        model = AlternatingLeastSquares(factors=factors, 
                                             regularization=regularization,
                                             iterations=iterations,  
                                             num_threads=num_threads)
        model.fit(csr_matrix(self.user_item_matrix).T.tocsr())
        
        return model

    def get_similar_items_recommendation(self, user, filter_ctm=True, N=5):
        """Рекомендуем товары, похожие на топ-N купленных юзером товаров"""
        #TODO: проверка пользователя на сущестование
        res = []
        top_N_items = self.top_purchases[self.top_purchases['user_id']==user]['item_id'].reset_index().item_id.tolist()[:N]
        for item in top_N_items:          
          top_similar_items = self.model.similar_items(self.itemid_to_id[item], 2)[1:]
          top_similar_item = id_to_itemid[top_simular_items[0]]
          if not(filter_ctm) or self.item_id_to_ctm[top_simular_item]==1: #Если ищем любой похожий товар или первый похожий СТМ
              res.append(top_similar_item)
          else: #Если нуже только товар СТМ, то ищем его пока не будет найден
              for similar_item in top_similar_items[1:]: 
                similar_item_id = id_to_itemid[similar_item]
                if self.item_id_to_ctm[similar_item_id]==1:
                   res.append(similar_item_id)      
                   break 
        assert len(res) == N, 'Количество рекомендаций != {}'.format(N)      
        return res
    
    def get_similar_users_recommendation(self, user, N=5):
        """Рекомендуем топ-N товаров, среди купленных похожими юзерами"""
        #TODO: проверка пользователя на сущестование
        res = []
        top_similar_users = self.model.top_similar_users(self.userid_to_id[user], N=N+1)[1:]
        for id in top_similar_users[::-1]:
          user_id = self.id_to_userid[id]
          items = self.top_purchases[self.top_purchases['user_id']== user_id]['item_id'].reset_index().item_id.tolist()          
          for item in items:
            if not(item in res):
              res.append(item)
              break
        assert len(res) == N, 'Количество рекомендаций != {}'.format(N)
        return res