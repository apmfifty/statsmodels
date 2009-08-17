"""examples for usage of F-test on linear restrictions in OLS

linear restriction is R \beta = 0
R is (nr,nk), beta is (nk,1) (in matrix notation)
"""

import numpy as np
import numpy.testing as npt
import models
from models.datasets.longley.data import load
from models.regression import OLS
from models import tools

data = load()
data.exog = tools.add_constant(data.exog)
res = OLS(data.endog, data.exog).fit()

# test pairwise equality of some coefficients
R2 = [[0,1,-1,0,0,0,0],[0, 0, 0, 0, 1, -1, 0]]
Ftest = res.Fcontrast(R2)
print repr((Ftest.F, Ftest.p_val)) #use repr to get more digits
# 9.740461873303655 0.0056052885317360301

##Compare to R (after running R_lm.s in the longley folder) looks good.
##
##> library(car)
##> linear.hypothesis(m1, c("GNP = UNEMP","POP = YEAR"))
##Linear hypothesis test
##
##Hypothesis:
##GNP - UNEMP = 0
##POP - YEAR = 0
##
##Model 1: TOTEMP ~ GNPDEFL + GNP + UNEMP + ARMED + POP + YEAR
##Model 2: restricted model
##
## Res.Df      RSS Df Sum of Sq      F   Pr(>F)
##1      9   836424
##2     11  2646903 -2  -1810479 9.7405 0.005605 **

# test all variables have zero effect
R = np.eye(7)[:-1,:]
Ftest0 = res.Fcontrast(R)
print repr((Ftest0.F, Ftest0.p_val))
print '%r' % res.F
npt.assert_almost_equal(res.F, Ftest0.F, decimal=9)
# values differ in 11th decimal, or 10th

ttest0 = res.Tcontrast(R[0,:])
print repr((ttest0.t, ttest0.p_val))

betatval = res.t()
betatval[0]
npt.assert_almost_equal(betatval[0], ttest0.t, decimal=15)

'''
# several ttests at the same time
# currently not checked for this, but it (kind of) works
>>> ttest0 = res.Tcontrast(R[:2,:])
>>> print repr((ttest0.t, ttest0.p_val))
(array([[ 0.17737603,         NaN],
       [        NaN, -1.06951632]]), array([[ 0.43157042,  1.        ],
       [ 1.        ,  0.84365947]]))

>>> ttest0 = res.Tcontrast(R)
>>> ttest0.t
array([[  1.77376028e-01,              NaN,              NaN,
                     NaN,  -1.43660623e-02,   2.15494063e+01],
       [             NaN,  -1.06951632e+00,  -1.62440215e+01,
         -1.78173553e+01,              NaN,              NaN],
       [             NaN,  -2.88010561e-01,  -4.13642736e+00,
         -4.06097408e+00,              NaN,              NaN],
       [             NaN,  -6.17679489e-01,  -7.94027056e+00,
         -4.82198531e+00,              NaN,              NaN],
       [  4.23409809e+00,              NaN,              NaN,
                     NaN,  -2.26051145e-01,   2.89324928e+02],
       [  1.77445341e-01,              NaN,              NaN,
                     NaN,  -8.08336103e-03,   4.01588981e+00]])
>>> betatval
array([ 0.17737603, -1.06951632, -4.13642736, -4.82198531, -0.22605114,
        4.01588981, -3.91080292])
>>> np.diag(ttest0.t)
array([ 0.17737603, -1.06951632, -4.13642736, -4.82198531, -0.22605114,
        4.01588981])
'''


ttest0 = res.Tcontrast(R2)
t2 = np.diag(ttest0.t)
t2a = np.r_[res.Tcontrast(np.array(R2)[0,:]).t, res.Tcontrast(np.array(R2)[1,:]).t]
print t2 - t2a
t2pval = np.diag(ttest0.p_val)
print '%r' % t2pval    #reject
# array([  9.33832896e-04,   9.98483623e-01])
print 'reject'
print '%r' % (t2pval < 0.05)

# Fcontrast needs 2-d currently
Ftest2a = res.Fcontrast(np.asarray(R2)[:1,:])
print repr((Ftest2a.F, Ftest2a.p_val))
Ftest2b = res.Fcontrast(np.asarray(R2)[1:2,:])
print repr((Ftest2b.F, Ftest2b.p_val))
# equality of ttest and Ftest
print t2a**2 - np.array((Ftest2a.F, Ftest2b.F))
npt.assert_almost_equal(t2a**2, np.array((Ftest2a.F, Ftest2b.F)))
#npt.assert_almost_equal(t2pval, np.array((Ftest2a.p_val, Ftest2b.p_val)))

# Why is there a huge difference in the pvalue comparing
# ttest and Ftest with a single row
# shouldn't this be the same ---> verify
# error in pvalue of Ftest, statistics are correct

nsample = 100
ncat = 4
sigma = 2
xcat = np.linspace(0,ncat-1, nsample).round()[:,np.newaxis]
dummyvar = (xcat == np.arange(ncat)).astype(float)

beta = np.array([0., 2, -2, 1])[:,np.newaxis]
ytrue = np.dot(dummyvar, beta)
X = tools.add_constant(dummyvar[:,:-1])
y = ytrue + sigma * np.random.randn(nsample,1)
mod = OLS(y[:,0], X)
res = mod.fit()
R = np.eye(ncat)[:-1,:]
Ftest = res.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))
R = np.atleast_2d([0, 1, -1, 2])
Ftest = res.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))

R = np.eye(ncat)[:-1,:]
ttest = res.Tcontrast(R)
print repr((np.diag(ttest.t), np.diag(ttest.p_val)))


R = np.atleast_2d([0, 1, 1, 2])
np.dot(R,res.params)
Ftest = res.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))
ttest = res.Tcontrast(R)
print repr((np.diag(ttest.t), np.diag(ttest.p_val)))
print repr((ttest.t, ttest.p_val))

R = np.atleast_2d([1, -1, 0, 0])
np.dot(R,res.params)
Ftest = res.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))
ttest = res.Tcontrast(R)
print repr((np.diag(ttest.t), np.diag(ttest.p_val)))
print repr((ttest.t, ttest.p_val))

R = np.atleast_2d([1, 0, 0, 0])
np.dot(R,res.params)
Ftest = res.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))
ttest = res.Tcontrast(R)
print repr((np.diag(ttest.t), np.diag(ttest.p_val)))
print repr((ttest.t, ttest.p_val))


# Example: 2 categories: replicate stats.glm and stats.ttest_ind

mod2 = OLS(y[xcat.flat<2][:,0], X[xcat.flat<2,:][:,(0,-1)])
res2 = mod2.fit()

R = np.atleast_2d([1, 0])
np.dot(R,res2.params)
Ftest = res2.Fcontrast(R)
print repr((Ftest.F, Ftest.p_val))
ttest = res2.Tcontrast(R)
print repr((np.diag(ttest.t), np.diag(ttest.p_val)))
print repr((ttest.t, ttest.p_val))

stats.glm(y[xcat<2].ravel(), xcat[xcat<2].ravel())
stats.ttest_ind(y[xcat==0], y[xcat==1])
