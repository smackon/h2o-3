import random

from h2o.estimators.xgboost import *
from tests import pyunit_utils

'''
The goal of this test is to compare h2oxgboost runs with different random seeds and the results should be repeatable
with the same random seeds.
'''
def random_seeds_test():
    assert H2OXGBoostEstimator.available() is True

    # train H2O XGBoost first
    higgs_h2o_train = h2o.import_file(pyunit_utils.locate('bigdata/laptop/higgs_train_imbalance_100k.csv'))
    higgs_h2o_train[0] = higgs_h2o_train[0].asfactor()
    higgs_h2o_test = h2o.import_file(pyunit_utils.locate('bigdata/laptop/higgs_test_imbalance_100k.csv'))
    higgs_h2o_test[0] = higgs_h2o_test[0].asfactor()
    myX = list(higgs_h2o_train.names)
    y = "response"
    myX.remove(y)

    seed1 = random.randint(1, 100000000000)
    seed2 = seed1+10
    h2oParams = {"ntrees":100, "max_depth":10, "learn_rate":0.7, "col_sample_rate_per_tree" : 0.9,
                 "min_rows" : 5, "score_tree_interval": 100, "seed":seed1}

    # train 2 models with the same seeds
    h2oModel1 = H2OXGBoostEstimator(**h2oParams)
    # gather, print and save performance numbers for h2o model
    h2oModel1.train(x=myX, y=y, training_frame=higgs_h2o_train)
    h2oPredict1 = h2oModel1.predict(higgs_h2o_test)
    h2oModel2 = H2OXGBoostEstimator(**h2oParams)
    # gather, print and save performance numbers for h2o model
    h2oModel2.train(x=myX, y=y, training_frame=higgs_h2o_train)
    h2oPredict2 = h2oModel2.predict(higgs_h2o_test)
    h2oParams2 = {"ntrees":100, "max_depth":10, "learn_rate":0.7, "col_sample_rate_per_tree" : 0.9,
                 "min_rows" : 5, "score_tree_interval": 100, "seed":seed2}
    h2oModel3 = H2OXGBoostEstimator(**h2oParams2)
    # gather, print and save performance numbers for h2o model
    h2oModel3.train(x=myX, y=y, training_frame=higgs_h2o_train)
    h2oPredict3 = h2oModel3.predict(higgs_h2o_test)

    # Result comparison in terms of prediction output.  In theory, h2oModel1 and h2oModel2 should be the same
    # h2oModel3 will be different from the other two models

    # compare the logloss
    assert abs(h2oModel1._model_json["output"]["training_metrics"]._metric_json["logloss"]-
                    h2oModel2._model_json["output"]["training_metrics"]._metric_json["logloss"])<1e-10, \
        "Model outputs should be the same with same seeds but are not!  Expected: {0}, actual: " \
        "{1}".format(h2oModel1._model_json["output"]["training_metrics"]._metric_json["logloss"],
                     h2oModel2._model_json["output"]["training_metrics"]._metric_json["logloss"])
    assert abs(h2oModel1._model_json["output"]["training_metrics"]._metric_json["logloss"]-
                    h2oModel3._model_json["output"]["training_metrics"]._metric_json["logloss"])>1e-10, \
        "Model outputs should be different with same seeds but are not!"

    # compare some prediction probabilities
    pyunit_utils.compare_frames_local(h2oPredict1[['p0', 'p1']], h2oPredict2[['p0', 'p1']], prob=0.1, tol=1e-6) # should pass
    try:
        pyunit_utils.compare_frames_local(h2oPredict1[['p0', 'p1']], h2oPredict3[['p0', 'p1']], prob=0.1, tol=1e-6) # should fail
        assert False, "Predict frames from two different seeds should be different but is not.  FAIL!"
    except:
        assert True



if __name__ == "__main__":
    pyunit_utils.standalone_test(random_seeds_test)
else:
    random_seeds_test()
