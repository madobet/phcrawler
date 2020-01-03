#!/usr/bin/env python
# 使用from __future__ import unicode_literals，
# 将模块中显式出现的所有字符串转为unicode类型，youtube-dl 也需要
# from __future__ imports must occur at the beginning of the file
from __future__ import unicode_literals

import os, fire # ,argparse
from os.path import join

from loguru import logger

from phcrawler._parser import *
from phcrawler.downloader import *

def Main(types, dir=os.getcwd(), proxy=''):
  '''PH Crawler PH 下载器
     Args:
       types: 指定要下载的内容类型，可选 webm 或 mp4。
       webm 下载 P 站上热门页面的缩略图；mp4 下载工作目录中 phlist.txt 文件指定的视频。phlist.txt 文件内每行一个 P 站 key，参考 https://github.com/madobet/phcrawler/blob/master/phlist.txt
       dir: 工作目录，phcrawler 会在 工作目录 中下载视频、写入日志以及寻找 phlist.txt。
            不指定则默认 当前目录 为 工作目录。
       proxy: 指定代理地址，只支持 HTTP 代理 (格式形如 http://127.0.0.1:1080)。
              不指定则默认读取环境变量 http_proxy 的值。
     Returns:
       Description of return values.
  '''

  if not proxy:
    # example:
    # proxies = {
    #     "http": "socks5://127.0.0.1:1080",
    #     "https": "socks5://127.0.0.1:1080",
    # }
    proxies = {
      'http':  os.environ.get('http_proxy'),
      'https': os.environ.get('http_proxy')
    }
  if proxy:
    proxies = {
      'http': proxy,
      'https': proxy
    }

  # logger.add( "%s.log" % __file__.rstrip('.py'),
  #   format="{time:MM-DD HH:mm:ss} {level} {message}")
  logger.add( join(dir, "phcrawler.log"),
    format="{time:MM-DD HH:mm:ss} {level} {message}")

  if proxies:
    logger.info('use proxy -> "%s" for http and "%s" for https' % (proxies['http'], proxies['https']))

  paths = ['webm', 'mp4']
  for path in paths:
    path = join(dir, path)
    if not os.path.exists(path):
        os.mkdir(path)
  if types == 'webm':
    # https://www.pornhub.com/categories
    urls = [
      'https://www.pornhub.com/video?o=tr', 'https://www.pornhub.com/video?o=ht',
      'https://www.pornhub.com/video?o=mv', 'https://www.pornhub.com/video'
    ]
    for url in urls:
      info_list = ListPage(url, proxies)
      for info in info_list:
        PHDownload(info['url'], info['key'], 'webm', dir, proxies)
  elif types == 'mp4':
    with open(join(dir, 'phlist.txt'), 'r') as file:
        keys = list(set(file.readlines()))
    for key in keys:
      key = key.strip() # 读进来的 key 带换行或空格必须移除
      if not key:
          continue
      url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key
      logger.info('download from -> {}', url)
      info_dict = DetailPage(url, key, proxies)
      # print('内容是 '+ info_dict['url'])
      for video_url in info_dict['url']:
        PHDownload(video_url, info_dict['title'], 'mp4', dir, proxies, key)
  else:
    return
  logger.info('finished !')

def entry():
  # - 目前用 fire 自动生成文档，但如果使用 argparse 标准库处理参数：
  # parser = argparse.ArgumentParser(description='PH Crawler')
  # parser.add_argument('type', metavar='(webm|mp4)', help='要下载的内容类型。指定 webm 下载热门页面的缩略图；指定 mp4 下载工作目录中 phlist.txt 文件指定的视频')
  # parser.add_argument('-d', '--dir', default = os.getcwd() + '/' ,help='视频保存目录，默认当前工作目录')
  # parser.add_argument('-p', '--proxy', help='指定代理地址，只支持 HTTP 代理 (如 http://127.0.0.1:1080)')
  #
  fire.Fire(Main)

if __name__ == '__main__':
  entry()
