
# try to find best transform T between two images
# use in movie stabilization
# using feature alignments doesn't seem to work very well with plain targets
# but ECC image alignment works


import matplotlib.pyplot as plt
import matplotlib.image as mpim
# import matplotlib.patches as patches
import numpy as np
# import scipy.ndimage as ndimage
# import scipy.misc as misc
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg



folder = 'alignments/'
file1 = folder + 'C2448604_centered_Violet.jpg'
file2 = folder + 'C2448610_centered_Blue.jpg'


# ECC image alignment
# https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/

# this works - the new aligned image aligns perfectly with image1

im1 = cv2.imread(file1) # values are 0-255
im2 = cv2.imread(file2) # values are 0-255
im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
im2_gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)
sz = im1.shape
warp_mode = cv2.MOTION_TRANSLATION

warp_matrix = np.eye(2, 3, dtype=np.float32)
number_of_iterations = 5000
termination_eps = 1e-10
criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)
# Run the ECC algorithm. The results are stored in warp_matrix.
(cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)
print warp_matrix
# [[ 1.          0.          0.0037005 ]
#  [ 0.          1.          0.00485788]]
# ? are these fractions of 800? (* 800 0.0037005) 2.96, (* 800 0.00485788) 3.88 maybe so
im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
# Show final results
cv2.imshow("Image 1", im1)
cv2.imshow("Image 2", im2)
cv2.imshow("Aligned Image 2", im2_aligned)
cv2.waitKey(0)
cv2.imwrite('foo.jpg', im2_aligned)






# Load files
# # im1 = cv2.imread(file1, cv2.IMREAD_GRAYSCALE) # values are 0-255
# # im2 = cv2.imread(file2, cv2.IMREAD_GRAYSCALE) # values are 0-255
# libimg.show(im1)
# img = cv2.imread(file1) # values are 0-255
# img = cv2.imread(file2) # values are 0-255
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# HARRIS corners
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
# finds lots of points in one image, way less in the other - not robust
# gray = np.float32(gray)
# dst = cv2.cornerHarris(gray,2,3,0.04)
# dst = cv2.dilate(dst,None)
# img[dst>0.01*dst.max()]=[0,0,255]
# libimg.show(img)

# SHI-TOMASI corners
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html
# finds lots - might work for aligning images
# might not though - not extremely robust, but better than others here
# gray = np.float32(gray)
# corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
# corners = np.int0(corners)
# for i in corners:
    # x,y = i.ravel()
    # cv2.circle(img,(x,y),3,255,-1)
# libimg.show(img)

# SIFT features
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_sift_intro/py_sift_intro.html
# patented
# just finds the one centered on the target. approximately centered anyway.
# and not sure how it would compare with hough - eg gaps, large targets
# might work for aligning moon images eg miranda
# sift = cv2.SIFT()
# kp = sift.detect(gray,None)
# img2 = cv2.drawKeypoints(gray,kp,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# libimg.show(img2)

# SURF features
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_surf_intro/py_surf_intro.html
# patented
# in one image it found one feature, in another extremely similar it found two.
# so not sure how robust it would be. and need more features for alignment.
# surf = cv2.SURF(400)
# surf.upright = True
# kp, des = surf.detectAndCompute(img,None)
# img2 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)
# libimg.show(img2)

# FAST features
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_fast/py_fast.html
# not as consistent at finding edges as harris corner detector -
# one image had most on one side, the other similar image had very different set of points
# fast = cv2.FastFeatureDetector()
# fast.setBool('nonmaxSuppression',0)
# kp = fast.detect(img,None)
# img2 = cv2.drawKeypoints(img, kp, color=(0,0,255))
# libimg.show(img2)

# STAR features
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_brief/py_brief.html
# finds halo of points way outside the target - nonrobust
# star = cv2.FeatureDetector_create("STAR")
# kp = star.detect(img,None)
# img2 = cv2.drawKeypoints(img, kp, color=(0,0,255))
# libimg.show(img2)

# ORB features
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_orb/py_orb.html
# whoa... this works perfectly - points all along edges of target!
# orb = cv2.ORB()
# kp = orb.detect(img,None)
# kp, des = orb.compute(img, kp)
# img2 = cv2.drawKeypoints(img,kp,color=(0,0,255), flags=0)
# libimg.show(img2)



# # MATCHING ORB features
# # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_matcher/py_matcher.html
# # img1 = cv2.imread(file1) # values are 0-255
# # img2 = cv2.imread(file2) # values are 0-255
# img1 = cv2.imread(file1,0) # values are 0-255
# img2 = cv2.imread(file2,0) # values are 0-255
# # make canny edges
# # upper = 200
# # lower = upper/2
# # img1 = cv2.Canny(img1, lower, upper)
# # img2 = cv2.Canny(img2, lower, upper)
# nFeatures = 200
# orb = cv2.ORB(nFeatures)
# # kp1 = orb.detect(img1,None)
# # kp1, des1 = orb.compute(img1, kp1)
# # kp2 = orb.detect(img2,None)
# # kp2, des2 = orb.compute(img2, kp2)
# kp1, des1 = orb.detectAndCompute(img1, None)
# kp2, des2 = orb.detectAndCompute(img2, None)
# img1b = cv2.drawKeypoints(img1,kp1,color=(0,0,255), flags=0)
# img2b = cv2.drawKeypoints(img2,kp2,color=(0,0,255), flags=0)
# libimg.show(img1b)
# libimg.show(img2b)
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# matches = bf.match(des1,des2)
# matches = sorted(matches, key = lambda x:x.distance)
# # note how scrambled the matches are - don't seem to use edge direction in descriptors
# img3 = libimg.drawMatches(img1,kp1,img2,kp2,matches[:10])
# # libimg.show(img3)
# # so now what - what is the transform x y between the feature sets?
# good = matches
# src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
# dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
# M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
# matchesMask = mask.ravel().tolist()
# print matchesMask
# print M
# # M = cv2.estimateRigidTransform(src_pts,dst_pts,False)
# # print M

# # nowork
# # FLANN_INDEX_KDTREE = 0
# # index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
# # search_params = dict(checks = 50)
# # flann = cv2.FlannBasedMatcher(index_params, search_params)
# # matches = flann.knnMatch(des1,des2,k=2)
# # # store all the good matches as per Lowe's ratio test.
# # good = []
# # for m,n in matches:
# #     if m.distance < 0.7*n.distance:
# #         good.append(m)
# # MIN_MATCH_COUNT = 10
# # if len(good)>MIN_MATCH_COUNT:
# #     src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
# #     dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
# #     M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
# #     matchesMask = mask.ravel().tolist()
# #     h,w = img1.shape
# #     pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
# #     dst = cv2.perspectiveTransform(pts,M)
# #     img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
# # else:
# #     print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
# #     matchesMask = None
# # # Finally we draw our inliers (if successfully found the object) or matching keypoints (if failed).
# # # draw_params = dict(matchColor = (0,255,0), # draw matches in green color
# #                    # singlePointColor = None,
# #                    # matchesMask = matchesMask, # draw only inliers
# #                    # flags = 2)
# # # img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
# # img3 = libimg.drawMatches(img1,kp1,img2,kp2,good)
# # libimg.show(img3)






