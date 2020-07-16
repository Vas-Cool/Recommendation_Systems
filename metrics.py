import numpy as np

### 1. Hit rate@k = (был ли хотя бы 1 релевантный товар среди топ-k рекомендованных)
def hit_rate_at_k(recommended_list, bought_list, k=5):
    
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list[:k])
        
    flags = np.isin(bought_list, recommended_list)
    hit_rate = (flags.sum() > 0) * 1
    
    return hit_rate

def precision(recommended_list, bought_list):
    
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list)
    
    flags = np.isin(bought_list, recommended_list)  # [False, False, True, True]
    
    precision = flags.sum() / len(recommended_list)
    
    return precision


def precision_at_k(recommended_list, bought_list, k=5):
    
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list)
    
    bought_list = bought_list  # Тут нет [:k] !!
    recommended_list = recommended_list[:k]
    
    flags = np.isin(bought_list, recommended_list)
    
    precision = flags.sum() / len(recommended_list)
    
    return precision
	
	
### 2. Money Precision@k = (revenue of recommended items @k that are relevant) / (revenue of recommended items @k)  	
def money_precision_at_k(recommended_list, bought_list, prices_recommended, k=5):
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list[:k])
    prices_recommended = np.array(prices_recommended[:k])
    flags = np.isin(recommended_list, bought_list)
    prices = flags * prices_recommended 
    precision = prices.sum()/ prices_recommended.sum()
    return precision
	
### 3. Recall@k = (# of recommended items @k that are relevant) / (# of relevant items)  
def recall_at_k(recommended_list, bought_list, k=5):    
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list[:k])    
    flags = np.isin(bought_list, recommended_list)    
    recall = flags.sum() / len(bought_list)    
    return recall


### 4. Money Recall@k = (revenue of recommended items @k that are relevant) / (revenue of relevant items)
def money_recall_at_k(recommended_list, bought_list, prices_recommended, prices_bought, k=5):    
    bought_list = np.array(bought_list)
    prices_bought = np.array(prices_bought)
    recommended_list = np.array(recommended_list[:k]) 
    prices_recommended = np.array(prices_recommended[:k])
    choice_price_recommended_list = np.isin(recommended_list, bought_list) * prices_recommended
    recall = choice_price_recommended_list.sum() / prices_bought.sum()       
    return recall
	
### 5. Reciprocal Rank
def reciprocal_rank(recommended_list, bought_list):
    bought_list = np.array(bought_list)
    recommended_list = np.array(recommended_list)  
    first_item = np.min(np.where(np.isin(recommended_list, bought_list)))
    result = 1/(first_item + 1)
    return result