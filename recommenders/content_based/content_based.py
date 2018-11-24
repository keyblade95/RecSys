"""
Content based recommender.
"""

from recommenders.distance_based_recommender import DistanceBasedRecommender
import utils.log as log
import numpy as np
import similaripy as sim
import data.data as data
from inout.importexport import exportcsv
import time

class ContentBasedRecommender(DistanceBasedRecommender):
    """
    Computes the recommendations for a user by looking for the most similar items that he
    has already interacted with.
    """

    def __init__(self):
        super(ContentBasedRecommender, self).__init__()
        self.name = 'content_based'

    def fit(self, icm, k, distance, shrink=0, threshold=0, alpha=None, beta=None, l=None, c=None):
        """
        Initialize the model and compute the similarity matrix S with a distance metric.
        Access the similarity matrix using: self._sim_matrix

        Parameters
        ----------
        icm : csr_matrix
            The ICM matrix of shape (number_items, number_features).
        k : int
            K nearest neighbour to consider.
        distance : str
            One of the supported distance metrics, check collaborative_filtering_base constants.
        shrink : float, optional
            Shrink term used in the normalization
        alpha: float, optional, included in [0,1]
        beta: float, optional, included in [0,1]
        l: float, optional, balance coefficient used in s_plus distance, included in [0,1]
        c: float, optional, cosine coefficient, included in [0,1]
        """
        return super(ContentBasedRecommender, self).fit(matrix=icm, k=k, distance=distance, shrink=shrink, threshold=threshold, implicit=False, alpha=alpha, beta=beta, l=l, c=c)
    

    def run(self, distance, urm=None, icm=None, urm_test=None, targetids=None, k=100, shrink=10, threshold=0,
        alpha=None, beta=None, l=None, c=None, with_scores=False, export=True, verbose=True):
        """
        Run the model and export the results to a file

        Parameters
        ----------
        distance : str, distance metric
        urm : csr matrix, URM. If None, used: data.get_urm_train(). This should be the
            entire URM for which the targetids corresponds to the row indexes.
        icm : csr matrix, ICM. If None, used: data.get_icm()
        urm_test : csr matrix, urm where to test the model. If None, use: data.get_urm_test()
        targetids : list, target user ids. If None, use: data.get_target_playlists()
        k : int, K nearest neighbour to consider
        shrink : float, shrink term used in the normalization
        threshold : float, all the values under this value are cutted from the final result

        Returns
        -------
        recs: (list) recommendations
        map10: (float) MAP10 for the provided recommendations
        """
        _urm = data.get_urm_train()
        _icm = data.get_icm()
        _urm_test = data.get_urm_test()
        _targetids = data.get_target_playlists()
        #_targetids = data.get_all_playlists()

        start = time.time()

        urm = _urm if urm is None else urm
        icm = _icm if icm is None else icm
        urm_test = _urm_test if urm_test is None else urm_test
        targetids = _targetids if targetids is None else targetids

        self.fit(icm=icm, k=k, distance=distance, shrink=shrink, threshold=threshold, alpha=alpha, beta=beta, l=l, c=c)
        recs = self.recommend_batch(userids=targetids, urm=urm, N=10, verbose=verbose)

        map10 = None
        if len(recs) > 0:
            map10 = self.evaluate(recs, test_urm=urm_test, verbose=verbose)
        else:
            log.warning('No recommendations available, skip evaluation')

        if export:
            exportcsv(recs, path='submission', name='{}_{}'.format(self.name,distance), verbose=verbose)

        if verbose:
            log.info('Run in: {:.2f}s'.format(time.time()-start))
        
        return recs, map10


    def test(self, distance=DistanceBasedRecommender.SIM_SPLUS, k=100, shrink=0, threshold=0, alpha=0.5, beta=0.5, l=0.5, c=0.5):
        """
        Test the model without saving the results. Default distance: SPLUS
        """
        return self.run(distance=distance, k=k, shrink=shrink, threshold=threshold, alpha=alpha, beta=beta, l=l, c=c, export=False)


"""
If this file is executed, test the SPLUS distance metric
"""
if __name__ == '__main__':
    model = ContentBasedRecommender()
    model.test()
