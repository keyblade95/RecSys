import numpy as np
import implicit
from scipy.sparse import load_npz
from data import Data
from helpers import model_bridge as M
from helpers.export import Export
from election_methods import ElectionMethods

# load data
d = Data()
targetUsersIds = d.target_playlists_df['playlist_id'].values

# get item_user matrix by transposing the URM matrix and convert it to COO
URM = load_npz('../dataset/saved_matrices/sp_urm.npz')
item_user_data = URM.transpose().tocoo()
print('> data loaded')

# initialize a model
model = implicit.bpr.BayesianPersonalizedRanking(factors=300, iterations=1000, learning_rate=0.01)

# train the model on a sparse matrix of item/user/confidence weights
model.fit(item_users=item_user_data)

# build recommendations array
recommendations = M.array_of_recommendations(model, target_user_ids=targetUsersIds, urm=URM)

#test borda====
arr_rec = []
weights = []
for i in range(4):
    arr_rec[i] = recommendations
    weights[i] = 0.25

r = ElectionMethods.borda_count(recommendations, weights)


# export
Export.export(np.array(recommendations), path='../submissions/')
print("> exported")