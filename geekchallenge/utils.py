#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'AshIn'

def deal_img(img):
    '''
        将图片转换为固定尺寸
    '''
    import Image
    default_img = Image.open(img)
    new_img = default_img.resize((240, 240), Image.BILINEAR)
    return new_img

def hash_answer(answer):
    import hashlib
    hashed_answer = hashlib.sha1(answer.encode('utf-8').encode('hex')).hexdigest()
    return hashed_answer

