import os, subprocess, requests, youtube_dl
from os.path import join

from clint.textui import progress

from loguru import logger

from phcrawler import _parser

def PHDownload(url, name, filetype, dir=os.getcwd(), proxies={}, key='none'):
  folderpath = join(dir, '%s/' % (filetype))
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
      response = requests.get(url, headers=_parser.headers, proxies=proxies, stream=True)
      with open(filepath, "wb") as file:
        total_length = int(response.headers.get('content-length'))
        for ch in progress.bar(response.iter_content(chunk_size=2391975),
                               expected_size=(total_length / 1024) + 1):
          if ch:
            file.write(ch)
    elif filetype == 'mp4':
      # 使用 aria2
      if 'http' in proxies:
        proxy_opt = '--all-proxy=' + proxies['http']
      else:
        proxy_opt = ''
      subprocess.call([
          'aria2c','-c',
          '-x%s' % os.cpu_count(),
          '-j%s' % os.cpu_count(),
          '-s%s' % os.cpu_count(),
          '-d'+folderpath, '-o'+filename, proxy_opt,
          '--no-conf=true', '--file-allocation=none', url
      ], shell=False)
      logger.info('download success -> %s' % filepath)

      # from tqdm import tqdm
      # with open(filepath, "wb") as handle:
      #     for data in tqdm(response.iter_content()):
      #         handle.write(data)

      # rep = requests.get(url, headers=_parser.headers, proxies=proxies)
      # with open(filepath, 'wb') as file:
      #     file.write(rep.content)
      # urllib.request.urlretrieve(url, '%s' % filepath)

def TBDownload(url, dir=os.getcwd(), proxies={}):
  from phcrawler.__ydl__ import ydl_opts
  ydl_opts['proxy'] = proxies['http']
  ydl_opts['outtmpl'] = join(dir,'%(title)s.%(ext)s')
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
