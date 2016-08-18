
"""
Obtain the best translation parameters tx,ty for a given set of data, using RANSAC.

The data is a set of point pairs, eg
[[[x1,y1],[x1',y1']],
 [[x2,y2],[x2',y2']],
 ...
 ]

The output is [tx,ty], which can be used to predict x',y' given x,y, i.e.
  x' = x + tx
  y' = y + ty

See https://en.wikipedia.org/wiki/RANSAC#Algorithm
"""

import random


# debug=True
debug=False


def getModelFromData(data):
    """
    get translation model from data - data consists of sets of point pairs (p,p')
    p' = p + (tx,ty)
    p = (x,y)
    p' = (x',y')
    the translation model is just [tx,ty]
    a translation matrix T would be [[1 0 tx] [0 1 ty]]
    """
    sumdeltax = 0
    sumdeltay = 0
    if data is None: return None
    for pair in data:
        p = pair[0]
        pprime = pair[1]
        x = p[0]
        y = p[1]
        xprime = pprime[0]
        yprime = pprime[1]
        deltax = xprime-x
        deltay = yprime-y
        sumdeltax += deltax
        sumdeltay += deltay
    npairs = len(data)
    avgdeltax = float(sumdeltax) / npairs
    avgdeltay = float(sumdeltay) / npairs
    tx = avgdeltax
    ty = avgdeltay
    model = [tx, ty]
    return model


def applyModel(model, p):
    """
    get p' = model(p)
    in this case,
      model=(tx,ty), p=(x,y), p'=(x',y'),
    and
      x'=x+tx, y'=y+ty
    """
    tx = model[0]
    ty = model[1]
    x = p[0]
    y = p[1]
    xprime = x + tx
    yprime = y + ty
    pprime = [xprime, yprime]
    return pprime


def getErrorPair(model, pair):
    """
    get error for the given pair of points and the model.
    ie calculate error = (p' - pcalc)**2,
    with pcalc = model * p
    """
    tx = model[0]
    ty = model[1]
    p = pair[0]
    pprime = pair[1]
    x = p[0]
    y = p[1]
    xprime = pprime[0]
    yprime = pprime[1]
    xcalc = x + tx
    ycalc = y + ty
    xdiff = xcalc-xprime
    ydiff = ycalc-yprime
    err = xdiff**2 + ydiff**2
    return err



def getRansacModel(data):
    """
    Get a model that fits the data, eliminating outliers. 
    data is a set of observed data point pairs.
    Returns tx,ty,modelOk
    
    Parameters
      minDataValues - the minimum number of data values required to fit the model
      maxIterations - the maximum number of iterations allowed in the algorithm
      maxDistanceSquared ~ distance in pixels squared from the predicted position
      minExtraDataPairs - the number of extra data values required to assert model fits data well
                          if 0, can get a ransac model with just minDataValues datapairs
    """
    minDataValues = 1
    maxIterations = 10
    # maxDistanceSquared = 16
    maxDistanceSquared = 25
    # maxDistanceSquared = 36
    # minExtraDataPairs = 0
    minExtraDataPairs = 1

    iteration = 1
    bestfit = None
    besterr = 1e9
    modelOk = True
    
    while (iteration < maxIterations):

        if debug: print 'iteration',iterations,'of',k

        # get n randomly selected values from data
        maybeinliers = random.sample(data, minDataValues)
        if debug: print 'maybeinliers',maybeinliers

        # maybemodel = model parameters fitted to maybeinliers
        maybemodel = getModelFromData(maybeinliers)
        if debug: print 'maybemodel',maybemodel

        # for every point in data not in maybeinliers
        #     if point fits maybemodel with an error smaller than t
        #          add point to alsoinliers
        otherData = [pair for pair in data if not pair in maybeinliers]
        if debug: print otherData
        alsoinliers = []
        for pair in otherData:
            err = getErrorPair(maybemodel, pair)
            if debug: print 'pair,err',pair, err
            if err<maxDistanceSquared:
                alsoinliers.append(pair)
        if debug: print 'alsoinliers',alsoinliers

        # if the number of elements in alsoinliers is >= d {
        if len(alsoinliers)>=minExtraDataPairs:
            # this implies that we may have found a good model
            # now test how good it is
            # bettermodel = model parameters fitted to all points in maybeinliers and alsoinliers
            consensusSet = list(maybeinliers) # copy
            consensusSet.extend(alsoinliers)
            if debug: print 'consensusSet',consensusSet
            bettermodel = getModelFromData(consensusSet)
            if debug: print 'bettermodel',bettermodel
            # thiserr = a measure of how well model fits these points
            #. thiserr =
            thiserr = 0
            for pair in data:
                err = getErrorPair(bettermodel, pair)
                thiserr += err
            if thiserr < besterr:
                bestfit = bettermodel
                besterr = thiserr
        iteration += 1

    # return bestfit
    if bestfit:
        return bestfit[0],bestfit[1],True
    else:
        return 0,0,False


if __name__=='__main__':

    # data is a set of pairs of x,y points
    # eg [ [[x,y],[x',y']], ... ]
    # eg
    # x,y is a feature point in the red channel image,
    # x',y' is that same feature point in the blue channel image
    data = [[[0,0],[10,5]],
            [[1,1],[11,8]],
            [[2,2],[12,9]],
            [[0,0],[3,20]], # an outlier
            ]
    
    # first get a naive model which includes all the data
    model = getModelFromData(data)
    print 'naivemodel',model
    
    # now get the ransac model, which excludes outliers
    model = getRansacModel(data)
    print 'ransacmodel',model


