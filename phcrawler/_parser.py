import re, requests, js2py
from lxml import etree
from loguru import logger

headers = {
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}

# PH parser
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


def ListPage(url, proxies={}):
  '''列举热门页面
    Returns:
      由 gif/webm 视频的 key 和 url 组成的字典的列表
  '''
  logger.info('crawling : %s' % url)
  resp = requests.get(url, headers=headers, proxies=proxies, verify=False)
  html = etree.HTML(resp.text)
  vkeys = html.xpath('//*[@class="phimage"]/div/a/@href')
  gif_keys = html.xpath('//*[@class="phimage"]/div/a/img/@data-mediabook')
  info_list = []
  for i in range(len(vkeys)):
    item = {}
    item['vkey'] = vkeys[i].split('=')[-1]
    item['gif_url'] = gif_keys[i]
    try:
      if 'ph' in item['vkey']:
        info_list.append({ 'url': item['gif_url'], 'key': item['vkey'] })
    except Exception as err:
      logger.error(err)
  return info_list


def DetailPage(url, key, proxies={}):
  '''获取页面详细信息
    Returns:
      title 和 url 列表组成的字典
  '''
  s = requests.Session()
  resp = s.get(url, headers=headers, proxies=proxies, verify=False)
  html = etree.HTML(resp.content)

  title = ''.join(html.xpath('//h1//text()')).strip()
  info_dict = {
    'title': title,
    'url': []
  }
  logger.info(title)
  js_temp = html.xpath('//script/text()')
  for j in js_temp:
    if 'flashvars' in j:
      js = ''.join(j.split('\n')[:-8])
      video_url = ExeJs(js)
      logger.info(video_url)
      info_dict['url'].append(video_url)
      continue
  return info_dict
