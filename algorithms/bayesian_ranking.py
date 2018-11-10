import numpy as np
import implicit
from scipy.sparse import load_npz
from data import Data
from helpers import model_bridge as M
from helpers.export import Export
from election_methods import ElectionMethods
from map_evaluation import evaluate_map




# load data
d = Data()
targetUsersIds = d.target_playlists_df['playlist_id'].values
# targetUsersIds = d.all_playlists['playlist_id'].values


# get item_user matrix by transposing the URM matrix and convert it to COO
URM = load_npz('../dataset/saved_matrices/sp_urm.npz')
item_user_data = URM.transpose().tocoo()
print('> data loaded')

# initialize a model
model = implicit.bpr.BayesianPersonalizedRanking(factors=1, iterations=1, learning_rate=0.01)

# train the model on a sparse matrix of item/user/confidence weights
model.fit(item_users=item_user_data)

# build recommendations array
recommendations = M.array_of_recommendations(model, target_user_ids=targetUsersIds, urm=URM)




#test borda====
recommendations = np.asarray(recommendations)

arr_rec = []
weights = np.zeros(4)
for i in range(4):
    arr_rec.append(recommendations)
    weights[i] = 0.25

r = ElectionMethods.borda_count(arr_rec, weights)


test_urm = load_npz('../dataset/saved_matrices/sp_urm_test_MAP.npz')
map = evaluate_map(recommendations, test_urm)
print('estimated map:',  map)


# export
Export.export(np.array(recommendations), path='../submissions/')
print("> exported")
