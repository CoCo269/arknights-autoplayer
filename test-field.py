# -*- coding:utf-8 -*-
import sys, os, functools, time
import cv2

#################################
READ_MODE = (cv2.IMREAD_GRAYSCALE, cv2.IMREAD_COLOR, cv2.IMREAD_UNCHANGED)

def resizeToDefault(img):
	th, tw = 576, 1024
	return cv2.resize(img, (tw, th), interpolation = cv2.INTER_AREA)
#################################

# os.system('adb connect {host}:{port}'.format(host='127.0.0.1', port=7555))
# os.system('adb shell screencap /data/arknights-screen.png')
# os.system('adb pull /data/arknights-screen.png {to}'.format(to='./tmp/arknights-screen.png'))

img = cv2.imread('./tmp/arknights-screen.png', READ_MODE[0])
img = resizeToDefault(img)

tmp = cv2.imread('./case-img/lvp.png', READ_MODE[0])

mres = cv2.matchTemplate(img, tmp, cv2.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(mres)

th, tw = tmp.shape[:2]
poslt = max_loc
posrb = (poslt[0]+tw,poslt[1]+th)
cut = cv2.rectangle(img, poslt, posrb, 255, 2)

print(mres)
print(min_val, max_val, min_loc, max_loc)

# cv2.imshow('show image', img)
# cut = cv2.resize(cut, (108, 64), interpolation = cv2.INTER_AREA)
cv2.imshow('show image', cut)
cv2.waitKey(0)
cv2.destroyAllWindows()
