import unittest
import random

import pandas as pd
import numpy as np


from mastml import mastml
from mastml import plot_helper, html_helper
from matplotlib.ticker import MaxNLocator

class SmokeTests(unittest.TestCase):

    def test_classification(self):
        mastml.mastml_run('tests/conf/classification.conf', 'tests/csv/three_clusters.csv',
                'results/classification')

    def test_regression(self):
        mastml.mastml_run('tests/conf/regression.conf', 'tests/csv/boston_housing.csv', 'results/regression')

    def test_generation(self):
        mastml.mastml_run('tests/conf/feature-gen.conf', 'tests/csv/feature-gen.csv',
                'results/generation')

class TestPlots(unittest.TestCase):
    """ don't mind the mismatched naming conventions for [true actual y_true] and [pred prediction
    y_pred] """

    def setUp(self):
        self.stats = [
                ('foo', 500000),
                ('bar', 123.45660923904908),
                ('baz', 'impossoble'),
                ('rosco', 123e-500),
                ('math', r"My long label with unescaped {\LaTeX} $\Sigma_{C}$ math" "\n"
                    r"continues here with $\pi$"),
                ]

    def test_plot_predicted_vs_true(self):
        y_pred = 100 * (np.arange(30) + np.random.random_sample((30,)) * 10 - 3) + 0.5
        y_true = np.arange(30)

        plot_helper.plot_predicted_vs_true(y_true, y_pred, 'pred-vs-true.png', self.stats)

    def test_residuals_histogram(self):
        y_pred = np.arange(30) + sum(np.random.random_sample((30,)) for _ in range(10)) - 3
        y_true = np.arange(30)
        plot_helper.plot_residuals_histogram(y_true, y_pred, 'residuals.png', self.stats)

    def test_confusion_matrix(self):
        y_true = np.random.randint(4, size=(50,))
        y_pred = y_true.copy()
        slices = [not bool(x) for x in np.random.randint(3, size=50)]
        y_pred[slices] = [random.randint(1, 3) for s in slices if s]

        names = ['a', 'b', 'c', 'f']
        y_pred = np.array([names[x] for x in y_pred] + ['a', 'a', 'a'])
        y_true = np.array([names[x] for x in y_true] + ['b', 'b', 'b'])

        plot_helper.plot_confusion_matrix(y_true, y_pred, 'confuse.png', self.stats)

    def test_best_worst(self):
        y_true = np.arange(30)
        y_pred = np.arange(30) + sum(np.random.random_sample((30,)) for _ in range(10)) - 3
        y_pred_bad = 0.2*np.arange(30) + 3*sum(np.random.random_sample((30,)) for _ in range(10)) - 3
        plot_helper.plot_best_worst(y_true, y_pred, y_pred_bad, 'best-worst.png', self.stats)

class TestHtml(unittest.TestCase):

    def test_image_list(self):
        #imgs = ['cf.png', 'rh.png', 'pred-vs-true.png']
        #html_helper.make_html(imgs, 'tests/csv/three_clusters.csv', 'tests/conf/fullrun.conf', 'oop.txt', './')
        html_helper.make_html('results/generation')
        html_helper.make_html('results/classification')
        html_helper.make_html('results/regression')

        

class TestRandomizer(unittest.TestCase):

    def test_shuffle_data(self):
        d = pd.DataFrame(np.arange(10).reshape(5,2))
        d.columns = ['a', 'b']
        r = Randomizer('b')
        r.fit(d)
        buffler = r.transform(d)
        good = r.inverse_transform(buffler)
        # this has a 1/120 chance of failing unexpectedly.
        self.assertFalse(d.equals(buffler))
        self.assertTrue(d.equals(good))

class TestNormalization(unittest.TestCase):

    def  test_normalization(self):
        d1 = pd.DataFrame(np.random.random((7,3)), columns=['a','b','c']) * 4 + 6 # some random data

        fn = FeatureNormalization(features=['a','c'], mean=-2, stdev=5)
        fn.fit()

        d2 = fn.transform(d1)
        self.assertTrue(set(d1.columns) == set(d2.columns))
        arr = d2[['a','c']].values
        #import pdb; pdb.set_trace()
        self.assertTrue(abs(arr.mean() - (-2)) < 0.001)
        self.assertTrue(abs(arr.std() - 5) < 0.001)

        d3 = fn.inverse_transform(d2)
        self.assertTrue(set(d1.columns) == set(d3.columns))
        self.assertTrue((abs(d3 - d1) < .001).all().all())
