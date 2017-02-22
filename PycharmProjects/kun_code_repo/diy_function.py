#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'

from hashlib import md5

digits = (
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
	'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
	'u', 'v', 'w', 'x', 'y', 'z'
	)


def ten_to_thirdysix(num):
	result = []
	if num == 0:
		return '0'
	while num > 0:
		num, b = divmod(num, 36)
		result .append(digits[b])

	return ''.join([str(x) for x in result[::-1]])


def thirdysix_to_ten(str_num):
	'''
		result = 0
		mul = 1
		for x in str_num[::-1]:
			result += mul * digits.index(x)
			mul *= 36
		return result
	'''
	return int(str_num, 36)


def generate_short_url(longurl):
	"""
    将长网址转换为短网址,算法：
    ① 将长网址用md5算法生成32位签名串，分为4段,，每段8个字符；
    ② 对这4段循环处理，取每段的8个字符, 将他看成16进制字符串与0x3fffffff(30位1)的位与操作，超过30位的忽略处理；
    ③ 将每段得到的这30位又分成6段，每5位的数字作为字母表的索引取得特定字符，依次进行获得6位字符串；
    ④ 这样一个md5字符串可以获得4个6位串，取里面的任意一个就可作为这个长url的短url地址。
    （出现重复的几率大约是n/(32^6) 也就是n/1,073,741,824，其中n是数据库中记录的条数）
    """

	base32 = 'abcdefghijklmnopqrstuvwxyz012345'
	m = md5()
	m.update(longurl)
	hexStr = m.hexdigest()
	hexLen = len(hexStr)
	subHexLen = hexLen / 8
	outUrl = []

	for i in range(0, subHexLen):
		subHex = '0x' + hexStr[i*8:(i+1)*8]
		res = 0x3FFFFFFF & int(subHex, 16)
		out = ''
		for j in range(6):
			val = 0x1F & res
			out += base32[val]
			res >>= 5

		outUrl.append(out)

	return outUrl


if __name__ == '__main__':
	pass