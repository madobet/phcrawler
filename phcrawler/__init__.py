#!/usr/bin/env python
import os
import re
import subprocess
from os.path import join
# import argparse

import js2py
import requests
from lxml import etree
from clint.textui import progress
from loguru import logger

headers = {
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}

def ListPage(url):
  logger.info('crawling : %s' % url)
  resp = requests.get(url, headers=headers, proxies=proxies, verify=False)
  html = etree.HTML(resp.text)
  vkeys = html.xpath('//*[@class="phimage"]/div/a/@href')
  gif_keys = html.xpath('//*[@class="phimage"]/div/a/img/@data-mediabook')
  for i in range(len(vkeys)):
    item = {}
    item['vkey'] = vkeys[i].split('=')[-1]
    item['gif_url'] = gif_keys[i]
    try:
      if 'ph' in item['vkey']:
        Download(item['gif_url'], item['vkey'], 'webm')
    except Exception as err:
      logger.error(err)

def DetailPage(url, key):
  s = requests.Session()
  resp = s.get(url, headers=headers, proxies=proxies, verify=False)
  html = etree.HTML(resp.content)

  title = ''.join(html.xpath('//h1//text()')).strip()
  logger.info(title)

  js_temp = html.xpath('//script/text()')
  for j in js_temp:
    if 'flashvars' in j:
      js = ''.join(j.split('\n')[:-8])
      videoUrl = ExeJs(js)
      logger.info(videoUrl)
      Download(videoUrl, title, 'mp4', key)
      continue

def ExeJs(js):
  flashvars = re.findall('flashvars_\d+', js)[0]
  res = js2py.eval_js(js + flashvars)
  if res.quality_1080p:
      return res.quality_1080p
  elif res.quality_720p:
      return res.quality_720p
  elif res.quality_480p:
      return res.quality_480p
  elif res.quality_240p:
      return res.quality_240p
  else:
      logger.error('parse url error')

def Download(url, name, filetype, key='none'):
  folderpath = join(prefix, '%s/' % (filetype))
  if key == 'none':
    filename = '%s.%s' % (name, filetype)
  else:
    filename = '[%s]%s.%s' % (key, name, filetype)
  filepath = join(folderpath, filename)
  if os.path.exists(filepath):
    logger.info('this file had been downloaded -> %s' % filepath)
    return
  else:
    if filetype == 'webm':
      # 使用 requests.get
      response = requests.get(url, headers=headers, proxies=proxies, stream=True)
      with open(filepath, "wb") as file:
        total_length = int(response.headers.get('content-length'))
        for ch in progress.bar(response.iter_content(chunk_size=2391975),
                               expected_size=(total_length / 1024) + 1):
          if ch:
            file.write(ch)
    elif filetype == 'mp4':
      # 使用 aria2
      core_n = os.cpu_count()
      if 'http' in proxies:
        subprocess.call([
          'aria2c','-c', '-x%s' % core_n, '-j%s' % core_n, '-s%s' % core_n,
          '-d'+folderpath, '-o'+filename,
          '--all-proxy='+proxies['http'],
          '--no-conf=true', '--file-allocation=none', url
        ], shell=False)
      else:
        subprocess.call([
          'aria2c','-c', '-x%s' % core_n, '-j%s' % core_n, '-s%s' % core_n,
          '-d'+folderpath, '-o'+filename,
          '--no-conf=true', '--file-allocation=none', url
        ], shell=False)

      # print("dl", "\'"+url+"\'", folderpath, filename)

      # from tqdm import tqdm
      # with open(filepath, "wb") as handle:
      #     for data in tqdm(response.iter_content()):
      #         handle.write(data)

      # rep = requests.get(url, headers=headers, proxies=proxies)
      # with open(filepath, 'wb') as file:
      #     file.write(rep.content)
      # urllib.request.urlretrieve(url, '%s' % filepath)
      logger.info('download success -> %s' % filepath)


def Run(types, dir=os.getcwd(), proxy=''):
  '''PH Crawler PH 下载器
     Args:
       types: (webm|mp4) 要下载的内容类型。webm 下载热门页面的缩略图；mp4 下载工作目录中 phlist.txt 文件指定的视频。phlist.txt 文件内每行一个 P 站 key，参考 https://github.com/madobet/phcrawler/blob/master/phlist.txt
       dir: 工作目录，phcrawler 会在 工作目录 中下载视频、写入日志以及寻找 phlist.txt。
            不指定则默认 当前目录 为 工作目录。
       proxy: 指定代理地址，只支持 HTTP 代理 (格式形如 http://127.0.0.1:1080)。
              不指定则默认读取环境变量 http_proxy 的值。
     Returns:
       Description of return values.
  '''

  global prefix
  # prefix = '/mnt/backup/Porn/PornHub/'

  global proxies
  # example:
  # proxies = {}
  # proxies = {
  #     "http": "socks5://127.0.0.1:1080",
  #     "https": "socks5://127.0.0.1:1080",
  # }
  proxies = {
    "http": "http://127.0.0.1:1913",
    "https": "http://127.0.0.1:1913",
  }

  prefix = dir
  
  if not proxy:
    proxy = os.environ.get('http_proxy')
  if proxy:
    proxies['http'] = proxy
    proxies['https'] = proxy
  else:
    proxies.clear

  # logger.add( "%s.log" % __file__.rstrip('.py'),
  #   format="{time:MM-DD HH:mm:ss} {level} {message}")
  logger.add( join(prefix, "phcrawler.log"),
    format="{time:MM-DD HH:mm:ss} {level} {message}")

  paths = ['webm', 'mp4']
  for path in paths:
    path = join(prefix, path)
    if not os.path.exists(path):
        os.mkdir(path)
  if types == 'webm':
    # https://www.pornhub.com/categories
    urls = [
      'https://www.pornhub.com/video?o=tr', 'https://www.pornhub.com/video?o=ht',
      'https://www.pornhub.com/video?o=mv', 'https://www.pornhub.com/video'
    ]
    for url in urls:
      ListPage(url)
  elif types == 'mp4':
    with open(join(prefix, 'phlist.txt'), 'r') as file:
        keys = list(set(file.readlines()))
    for key in keys:
      key = key.strip() # 读进来的 key 带换行或空格必须移除
      if not key:
          continue
      url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key
      logger.info('url: {}', url)
      DetailPage(url, key)
  else:
    return
  logger.info('finished !')
