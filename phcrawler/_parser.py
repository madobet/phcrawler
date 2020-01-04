import re, os, requests, js2py
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


def ListPage(url, file=os.path.join(os.getcwd(), 'preview.list'), proxies={}):
    '''热门/分类/搜索等页面的预览信息（根据 url 区分）
      Returns:
        由 gif/webm 视频的 key 和 url 组成的字典的列表
    '''
    logger.info('crawling : %s' % url)
    resp = requests.get(url, headers=headers, proxies=proxies, verify=False)
    html = etree.HTML(resp.text)
    titles = html.xpath('//*[@class="phimage"]/div/a/img/@alt')
#   titles = html.xpath('//*[@class="phimage"]/div/a/@data-title')    # 不行！
    raw_keys = html.xpath('//*[@class="phimage"]/div/a/@href')
    urls = html.xpath('//*[@class="phimage"]/div/a/img/@data-mediabook')
    info_list = []
    for i in range(len(raw_keys)):
      item = {
          # 标题中的 / 或 \ 容易导致文件系统把文件名的一部分当目录处理
          'title': titles[i].replace('/','_').replace('\\','_'),
          'url': urls[i],
          'key': raw_keys[i].split('viewkey=')[-1]
      }
      try:
        if 'ph' in item['key']:
          link = 'https://www.pornhub.com/view_video.php?viewkey=%s' % item['key']
          if file:
              with open(file,'a') as f:
                  f.write('# %s\n' % item['title'])
                  f.write('# %s\n' % link)
          info_list.append(item)
          print('[%s] ' % item['key'] + item['title'])
      except Exception as err:
        logger.error(err)
    return info_list


def DetailPage(url, key, proxies={}):
    '''获取页面详细信息
      Returns:
        title 和 url 列表组成的字典
    '''
    resp = requests.Session().get(url, headers=headers, proxies=proxies, verify=False)
    html = etree.HTML(resp.content)

    info_dict = {
      'title': ''.join(html.xpath('//h1//text()')).strip(),
      'url': []
    }
    for j in html.xpath('//script/text()'):
        if 'flashvars' in j:
          js = ''.join(j.split('\n')[:-8])
          video_url = ExeJs(js)
          logger.info(video_url)
          info_dict['url'].append(video_url)
          continue
    logger.info(info_dict['title'])
    return info_dict

# 无用函数，参考: https://github.com/eqblog/pornhub- 制成
def CatePage(cat, file=os.path.join(os.getcwd(), 'url.txt'), proxies={}):
    from bs4 import BeautifulSoup as bs
    page=1
    while page<=10:
        base_page='https://www.pornhub.com/categories/' + str(cat) + '?page=' + str(page)
        # base_page='https://www.pornhub.com/video/search?search=' + str(cat) + '&page=' + str(page)
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':base_page}
        get_base=requests.get(base_page, headers=headers, proxies=proxies)
        url_soup=bs(get_base.content,'lxml')
        for a_content in url_soup.select('.search-video-thumbs.videos li.videoBox'):
            a_content.a['class']='img js-pop'
            video_url='https://www.pornhub.com/' + re.findall(r' href="/(.*?)" title',str(a_content.a))[0]
            headers_1={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name','Referer':video_url}
            reqpage=requests.get(video_url, headers=headers_1, proxies=proxies)
            video_tittle=re.findall(r'<span class="inlineFree">(.*?)</span>',str(reqpage.content,'utf-8',errors='ignore'))[0]
            try:
                with open(file,'a') as f:
                    f.write('# ' + video_tittle + '\n')
                    f.write('# ' + video_url + '\n')
                    print(video_tittle + ': ' + video_url)
            except IndexError:
                print('invalid url')
                pass
        page+=1

