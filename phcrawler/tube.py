#!/usr/bin/env python
import os
import re
import subprocess
from pathlib import Path
from os.path import join

import fire
from loguru import logger

from __future__ import unicode_literals
import youtube_dl

headers = {
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}

# 如果代理不稳定，不推荐使用
#
# proxies example:
# proxies = {}
# proxies = {
#     "http": "socks5://127.0.0.1:1080",
#     "https": "socks5://127.0.0.1:1080",
# }
proxies = {
  "http": "http://127.0.0.1:1913",
  "https": "http://127.0.0.1:1913",
}

prefix = join(Path.home(), 'Downloads')

ydl_opts = {
  'format': 'bestaudio/best',
  'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '192',
  }],
  'logger': TBLogger(),
  'progress_hooks': [TBHook],
}

class TBLogger(object):
  def debug(self, msg):
      pass

  def warning(self, msg):
      pass

  def error(self, msg):
      print(msg)

def TBHook(d):
  if d['status'] == 'finished':
    print('video downloaded, now converting ...')

def TBDownload(url, key='none'):
  if os.path.exists(filepath):
    logger.info('this file had been downloaded -> %s' % filepath)
    return

  if key == 'none':
    ydl_opts['']
    filename = '%s.%s' % (name, filetype)
  else:
    filename = '[%s]%s.%s' % (key, name, filetype)
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
