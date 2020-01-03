import os, youtube_dl
from os.path import join

# 代码参考 https://github.com/formateddd/pornhub

class TBLogger(object):
  def debug(self, msg):
      pass

  def warning(self, msg):
      pass

  def error(self, msg):
      print(msg)

def TBHook(d):
  if d['status'] == 'finished':
    print( (d['tmpfilename'],'downloaded, now converting ...') )

ydl_opts = {
  'verbose': True,
  'geo_bypass': True,
  'format': 'bestaudio/best',
  'outtmpl': join(os.getcwd(),'%(title)s.%(ext)s'),
  # restrictfilenames: Do not allow "&" and spaces in file names
  # writethumbnail:    Write the thumbnail image to a file
  # write_all_thumbnails:  Write all thumbnail formats to files
  # writesubtitles:    Write the video subtitles to a file
  # writeautomaticsub: Write the automatically generated subtitles to a file
  # subtitleslangs:    List of languages of the subtitles to download
  'proxy': '',
  'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '192',
  }],
  'external_downloader': 'aria2c',
  'logger': TBLogger(),
  'progress_hooks': [TBHook],
  # The following parameters are not used by YoutubeDL itself, they are used
  # by the downloader (see youtube_dl/downloader/common.py)
  'buffersize': '16K',
  'external_downloader_args': (
    '-x%s' % os.cpu_count(),
    '-j%s' % os.cpu_count(),
    '-s%s' % os.cpu_count(),
    '--no-conf=true', '--file-allocation=none'),
}
