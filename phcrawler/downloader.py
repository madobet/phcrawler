import os, subprocess, requests, youtube_dl
from os.path import join

from clint.textui import progress

from loguru import logger

from phcrawler import _parser

def PHDownload(url, name, filetype, dir=os.getcwd(), proxies={}, key='none'):
  if key == 'none':
    f_name = '%s.%s' % (name, filetype)
  else:
    f_name = '[%s]%s.%s' % (key, name, filetype)
  f_path = join(dir, f_name)
  # if os.path.exists(f_path):
  #   logger.info('file exist -> %s' % f_path)
  #   return
  # else:
  if filetype == 'webm':
    # 使用 requests.get
    response = requests.get(url, headers=_parser.headers, proxies=proxies, stream=True)
    with open(f_path, "wb") as file:
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
        '-d'+dir, '-o'+f_name, proxy_opt,
        '--no-conf=true', '--file-allocation=none', url
    ], shell=False)
    logger.info('download success -> %s' % f_path)

    # from tqdm import tqdm
    # with open(f_path, "wb") as handle:
    #     for data in tqdm(response.iter_content()):
    #         handle.write(data)

    # rep = requests.get(url, headers=_parser.headers, proxies=proxies)
    # with open(f_path, 'wb') as file:
    #     file.write(rep.content)
    # urllib.request.urlretrieve(url, '%s' % f_path)

def TBDownload(url, dir=os.getcwd(), proxies={}):
    class TBLogger(object):
      def debug(self, msg):
          pass

      def warning(self, msg):
          pass

      def error(self, msg):
          print(msg)

    def TBHook(d):
      if d['status'] == 'finished':
        print('downloaded, now converting ...')

    ydl_opts = {
      'verbose': True,
      'geo_bypass': True,
    #   'format': 'best',
      'outtmpl': join(dir,'%(title)s.%(ext)s'),
      # restrictfilenames: Do not allow "&" and spaces in file names
      # writethumbnail:    Write the thumbnail image to a file
      # write_all_thumbnails:  Write all thumbnail formats to files
      # writesubtitles:    Write the video subtitles to a file
      # writeautomaticsub: Write the automatically generated subtitles to a file
      # subtitleslangs:    List of languages of the subtitles to download
      'proxy': proxies['http'],
    #   'postprocessors': [{
    #       'key': 'FFmpegExtractAudio',
    #       'preferredcodec': 'mp3',
    #       'preferredquality': '192',
    #   }],
    #   'logger': TBLogger(), # logger 有问题
      'progress_hooks': [TBHook],
      # The following parameters are not used by YoutubeDL itself, they are used
      # by the downloader (see youtube_dl/downloader/common.py)
      'external_downloader': 'aria2c',
      'buffersize': '16K',
      'external_downloader_args': [
        '-x%s' % os.cpu_count(),
        '-j%s' % os.cpu_count(),
        '-s%s' % os.cpu_count(),
        '--no-conf=true', '--file-allocation=none' ]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])
