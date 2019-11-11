# -*- coding:utf-8 -*-
import sys, os, functools, time, traceback, random, cv2

UserConfig = {
	'adb' : {
		'host' : '127.0.0.1',
		'port' : 7555,
	},
	'task' : {
		'loop' : 1000,
	},
}

SystemConfig = {
	'match' : {
		'case-path' : './case-img',
		'case-map' : {
			'bgA' : 'bgA.png',
			'bgB' : 'bgB.png',
			'end' : 'end.png',
			'lvp' : 'lvp.png',
			'rcv' : 'rcv.png', # TODO: 仅限理智药水
		}, 
		'case-after' : {
			'rcv' : 'rcv-bt.png',
		},
		'case-end' : 'end',
		'capture' : {
			'dir' : './tmp',
			'file' : 'arknights-screen.png',
		},
		'case-rate' : 0.6,
	},
	'default' : {
		'screen' : {
			'weight' : 1024,
			'height' : 576,
		},
	},
	'clock' : {
		'interval' : 3,
	}
}

LogN = functools.partial(print, '[Info ] ')
LogW = functools.partial(print, '[Warn ] ')
LogE = functools.partial(print, '[Error] ')
LogD = functools.partial(print, '[Debug] ')

class AdbManager:
	def connect(self):
		self.host, self.port = UserConfig['adb']['host'], UserConfig['adb']['port']
		os.system('adb connect {host}:{port}'.format(host=self.host, port=self.port))
	def screenshot(self):
	    os.system('adb shell screencap /storage/emulated/0/{fn}'.format(fn=SystemConfig['match']['capture']['file']))
	    os.system('adb pull /storage/emulated/0/{fn} {to}'.format(fn=SystemConfig['match']['capture']['file'], to=SystemConfig['match']['capture']['dir']))
	    return '{dir}/{fn}'.format(dir=SystemConfig['match']['capture']['dir'], fn=SystemConfig['match']['capture']['file'])
	def click(self, pos):
		os.system('adb shell input tap {x} {y}'.format(x=pos[0], y=pos[1]))
	def disconnect(self):
		os.system('adb kill-server')

class MatchHandler:
	def __init__(self):
		self.READ_MODE = (cv2.IMREAD_GRAYSCALE, cv2.IMREAD_COLOR, cv2.IMREAD_UNCHANGED)
	def mapToPos(self, imgfn):
		if not os.path.exists(imgfn):
			LogW('screenshot file \{{fn}\} no exists ...'.format(fn=imgfn))
			return None, None
		screen = cv2.imread(imgfn, self.READ_MODE[0])
		rh, rw = screen.shape[:2]
		szrate = rw/SystemConfig['default']['screen']['weight']
		screen = self.__resizeToDefault(screen)
		for evt,fn in SystemConfig['match']['case-map'].items():
			poslu, plus = self.__checkAndGetMatchPosLeftUp(screen, fn)
			if not poslu:
				continue
			# 检查是否存在后续联动事件，若有则触发
			if evt in SystemConfig['match']['case-after']:
				poslu, plus = self.__checkAndGetMatchPosLeftUp(screen, SystemConfig['match']['case-after'][evt])
				if not poslu:
					continue
			return evt, tuple(map((lambda x:int(szrate*x)), self.__genRandomPosInBox(poslu, plus)))
		return None, None
	def __checkAndGetMatchPosLeftUp(self, screen, evtfn):
		evtfn = '{dir}/{fn}'.format(dir=SystemConfig['match']['case-path'], fn=evtfn)
		tmpt = cv2.imread(evtfn, self.READ_MODE[0])
		mtres = cv2.matchTemplate(screen, tmpt, cv2.TM_CCOEFF_NORMED)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(mtres)
		return (None, None) if max_val < SystemConfig['match']['case-rate'] else (max_loc, (tmpt.shape[1], tmpt.shape[0]))
	def __resizeToDefault(self, img):
		th, tw = SystemConfig['default']['screen']['height'], SystemConfig['default']['screen']['weight']
		return cv2.resize(img, (tw, th), interpolation = cv2.INTER_AREA)
	def __genRandomPosInBox(self, poslu, plus):
		return tuple(poslu[i]+random.random()*plus[i] for i in (0,1))

def Prepare():
	if not os.path.exists(SystemConfig['match']['case-path']):
		raise Exception('Can\' find <case-path> in configuration ...')
	if not os.path.exists(SystemConfig['match']['capture']['dir']):
		os.mkdir(SystemConfig['match']['capture']['dir'])

if __name__ == '__main__':
	# 准备执行环境
	Prepare()
	adb = AdbManager()
	handler = MatchHandler()
	# 启动 ADB
	try:
		adb.connect()
		# 执行循环任务
		cot = 0
		while 1:
			imgfn = adb.screenshot()
			evt, pos = handler.mapToPos(imgfn)
			if pos:
				LogN('Event <{evt}> hit at position <{pos}> ...'.format(evt=evt, pos=pos))
				adb.click(pos)
			if evt == SystemConfig['match']['case-end']:
				cot += 1
				LogN('No <{nid}> task finished ...'.format(nid=cot))
				if cot >= UserConfig['task']['loop']:
					break
			time.sleep(SystemConfig['clock']['interval'])
	except Exception as err:
		LogE('Task break off because errors...')
		traceback.print_exc()
	finally:
		# 关闭连接退出
		adb.disconnect()
	LogN('Task done...')
	quit()

