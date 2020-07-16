import numpy as np

def prefilter_items(data, take_n_popular=5000, bottom_mean_price=1, top_mean_price=30, alpha=0.9, max_week=92, threshold=0.001):
    """Предфильтрация товаров"""
        
    items_mean_price = data.groupby(['item_id'])[['sales_value', 'quantity']].sum().reset_index()
    items_mean_price['mean_price'] = items_mean_price['sales_value']/items_mean_price['quantity']    
    
    #Добавляет столбец по продажам с учетом временного периода
    data['value'] = data['sales_value'] / (1 + np.exp(alpha * (max_week - data['week_no'])))

    # 1. Удаление товаров, со средней ценой < 1$
    items_bottom_mean_price = items_mean_price[items_mean_price['mean_price']<bottom_mean_price].item_id.tolist()
    data = data[~data['item_id'].isin(items_bottom_mean_price)]
    # 2. Удаление товаров со средней ценой > 30$
    items_top_mean_price = items_mean_price[items_mean_price['mean_price']>top_mean_price].item_id.tolist()
    data = data[~data['item_id'].isin(items_top_mean_price)]
    
    # 3. Придумайте свой фильтр
    #Отбрасываем малозначимые продажи в прошлом
    data = data.loc[data['value']>threshold]
    
    # 4. Выбор топ-N самых популярных товаров (N = take_n_popular)
    popular_items = data.groupby('item_id')['quantity'].count().reset_index()
    popular_items.sort_values(by='quantity', ascending=False)
    data = data[~data['item_id'].isin(popular_items)]   

    return data