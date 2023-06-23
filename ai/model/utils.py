import numpy as np
import pandas as pd
import os
import bottleneck as bn
import torch
from scipy import sparse
from ast import literal_eval
from math import log, floor, ceil

def get_data(dataset, global_indexing=False):
    unique_sid = list()
    with open(os.path.join(dataset, 'unique_sid.txt'), 'r') as f:
        for line in f:
            unique_sid.append(line.strip())
    
    unique_uid = list()
    with open(os.path.join(dataset, 'unique_uid.txt'), 'r') as f:
        for line in f:
            unique_uid.append(line.strip())
            
    n_items = len(unique_sid)
    n_users = len(unique_uid)
    
    train_data = load_train_data(os.path.join(dataset, 'train.csv'), n_items, n_users, global_indexing=global_indexing)


    vad_data_tr, vad_data_te = load_tr_te_data(os.path.join(dataset, 'validation_tr.csv'),
                                               os.path.join(dataset, 'validation_te.csv'),
                                               n_items, n_users, 
                                               global_indexing=global_indexing)

    test_data_tr, test_data_te = load_tr_te_data(os.path.join(dataset, 'test_tr.csv'),
                                                 os.path.join(dataset, 'test_te.csv'),
                                                 n_items, n_users, 
                                                 global_indexing=global_indexing)
    
    data = train_data, vad_data_tr, vad_data_te, test_data_tr, test_data_te
    data = (x.astype('float32') for x in data)
    
    return data

def load_train_data(csv_file, n_items, n_users, global_indexing=False):
    tp = pd.read_csv(csv_file)
    
    n_users = n_users if global_indexing else tp['uid'].max() + 1

    rows, cols = tp['uid'], tp['sid']
    data = sparse.csr_matrix((np.ones_like(rows),
                             (rows, cols)), dtype='float64',
                             shape=(n_users, n_items))
    return data


def load_tr_te_data(csv_file_tr, csv_file_te, n_items, n_users, global_indexing=False):
    tp_tr = pd.read_csv(csv_file_tr)
    tp_te = pd.read_csv(csv_file_te)

    if global_indexing:
        start_idx = 0
        end_idx = len(unique_uid) - 1
    else:
        start_idx = min(tp_tr['uid'].min(), tp_te['uid'].min())
        end_idx = max(tp_tr['uid'].max(), tp_te['uid'].max())

    rows_tr, cols_tr = tp_tr['uid'] - start_idx, tp_tr['sid']
    rows_te, cols_te = tp_te['uid'] - start_idx, tp_te['sid']

    data_tr = sparse.csr_matrix((np.ones_like(rows_tr),
                             (rows_tr, cols_tr)), dtype='float64', shape=(end_idx - start_idx + 1, n_items))
    data_te = sparse.csr_matrix((np.ones_like(rows_te),
                             (rows_te, cols_te)), dtype='float64', shape=(end_idx - start_idx + 1, n_items))
    return data_tr, data_te

def ndcg(X_pred, heldout_batch, k=100):
    '''
    Normalized Discounted Cumulative Gain@k for binary relevance
    ASSUMPTIONS: all the 0's in heldout_data indicate 0 relevance
    '''
    batch_users = X_pred.shape[0]
    idx_topk_part = bn.argpartition(-X_pred, k, axis=1)
    topk_part = X_pred[np.arange(batch_users)[:, np.newaxis],
                       idx_topk_part[:, :k]]
    idx_part = np.argsort(-topk_part, axis=1)

    idx_topk = idx_topk_part[np.arange(batch_users)[:, np.newaxis], idx_part]

    tp = 1. / np.log2(np.arange(2, k + 2))

    e = 0.000001

    DCG = (heldout_batch[np.arange(batch_users)[:, np.newaxis],
                         idx_topk].toarray() * tp).sum(axis=1)
    IDCG = np.array([(tp[:min(n, k)]).sum()
                     for n in heldout_batch.getnnz(axis=1)]) + e
    return DCG / IDCG

def recall(X_pred, heldout_batch, k=100):
    batch_users = X_pred.shape[0]

    idx = bn.argpartition(-X_pred, k, axis=1)
    X_pred_binary = np.zeros_like(X_pred, dtype=bool)
    X_pred_binary[np.arange(batch_users)[:, np.newaxis], idx[:, :k]] = True

    e = 0.000001

    X_true_binary = (heldout_batch > 0).toarray()
    tmp = (np.logical_and(X_true_binary, X_pred_binary).sum(axis=1)).astype(
        np.float32)
    #-------------------------
    # print('tmp :', len(tmp))
    # print('np.minimum(k, X_true_binary.sum(axis=1) :',len(np.minimum(k, X_true_binary.sum(axis=1))))
    #-------------------------
    recall = tmp / np.minimum(k, X_true_binary.sum(axis=1) + e)
    return recall

def load_n_items(dataset):
        unique_sid = list()
        with open(os.path.join(dataset, 'unique_sid.txt'), 'r') as f:
            for line in f:
                unique_sid.append(line.strip())
        n_items = len(unique_sid)
        return n_items

def sparse2torch_sparse(data):
    """
    Convert scipy sparse matrix to torch sparse tensor with L2 Normalization
    This is much faster than naive use of torch.FloatTensor(data.toarray())
    https://discuss.pytorch.org/t/sparse-tensor-use-cases/22047/2
    """
    samples = data.shape[0]
    features = data.shape[1]
    coo_data = data.tocoo()
    indices = torch.LongTensor([coo_data.row, coo_data.col])
    row_norms_inv = 1 / np.sqrt(data.sum(1))
    row2val = {i : row_norms_inv[i].item() for i in range(samples)}
    values = np.array([row2val[r] for r in coo_data.row])
    t = torch.sparse.FloatTensor(indices, torch.from_numpy(values).float(), [samples, features])
    return t

def naive_sparse2tensor(data):
    return torch.FloatTensor(data.toarray())

def numerize_for_infer(tp, profile2id, show2id):
    uid = tp['handle'].apply(lambda x: profile2id[str(x)])
    sid = tp['solved_problem'].apply(lambda x: show2id[str(x)])
    return pd.DataFrame(data={'uid': uid, 'sid': sid}, columns=['uid', 'sid'])

# 문자열을 리스트로 변환
def str_to_list(x):
    try:
        return literal_eval(x)
    except: #해당 값이 null값이거나 오류가 있을 때, None을 return 하기
        return None
    
# 딕셔너리에서 키값만 반환
def dic_to_list(x):
    try:
        temp = []
        for i in x:
            temp.append(i["key"])
        if not temp:
            return None
        else:
            return temp
    except: #해당 값이 null값이거나 오류가 있을 때, None을 return 하기
        return None
    
def numerize(tp, profile2id, show2id):
    uid = tp['handle'].apply(lambda x: profile2id[x])
    sid = tp['solved_problem'].apply(lambda x: show2id[x])
    return pd.DataFrame(data={'uid': uid, 'sid': sid}, columns=['uid', 'sid'])

def split_train_test_proportion(data, test_prop=0.2):
    '''
    data -> DataFrame
    
    train과 test를 8:2 비율로 나눠주는 함수.
    '''
    data_grouped_by_user = data.groupby('handle')
    tr_list, te_list = list(), list()

    np.random.seed(98765)
    
    for _, group in data_grouped_by_user:
        n_items_u = len(group)
        
        if n_items_u >= 5:
            idx = np.zeros(n_items_u, dtype='bool') # 'False'가 n_items_u개 만큼 채워진 array
            
            # n_items_u개 중에서 20%의 인덱스를 랜덤으로 뽑아서 해당 인덱스를 'True'로 바꿈
            idx[np.random.choice(n_items_u, size=int(test_prop * n_items_u), replace=False).astype('int64')] = True
                    
            tr_list.append(group[np.logical_not(idx)]) # 'False'인 것을 tr_list에 추가
            te_list.append(group[idx]) # 'True'인 것을 te_list에 추가
        
        else:
            tr_list.append(group)
    
    data_tr = pd.concat(tr_list)
    data_te = pd.concat(te_list)

    return data_tr, data_te
                
def min_max(lv):
    if lv <= 5:
        return 0, 7
    elif lv <= 10:
        return 5, 12
    elif lv <= 13:
        return 8, 16
    elif lv <= 15:
        return 11, 18
    else:
        return (floor(lv-log(lv, 2)), ceil(lv+log(lv, 3)))
    
def infer(user, item, dict_user_lv, dict_item_lv, id2show, infer_cnt):
    pred = np.array([])
    user_lv = dict_user_lv[user]
    cnt = 0
    mini, maxi = min_max(user_lv)
    item = sorted(item, reverse=True)
    for i in item:
        item_lv = dict_item_lv[int(id2show[i])]
        if mini <= item_lv <= maxi:
            pred = np.append(pred, i)
            cnt += 1
    
        if cnt == infer_cnt:
            return pred
    else:
        # print('else user :', user)
        if len(pred) < infer_cnt:
            for i in item:
                if i not in pred:
                    pred = np.append(pred, i)

                if len(pred) == infer_cnt:
                    return np.array(pred)
                
def de_numerize(tp, re_p2id, re_s2id):
    uid2 = tp['user'].apply(lambda x: re_p2id[x])
    sid2 = tp['item'].apply(lambda x: re_s2id[x])
    return pd.DataFrame(data={'uid': uid2, 'sid': sid2}, columns=['uid', 'sid'])