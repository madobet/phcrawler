#!/usr/bin/env python
# 使用from __future__ import unicode_literals，
# 将模块中显式出现的所有字符串转为unicode类型，youtube-dl 也需要
# from __future__ imports must occur at the beginning of the file
from __future__ import unicode_literals

import os, argparse
from os.path import join

from loguru import logger

from phcrawler._parser import *
from phcrawler.downloader import *

def entry():
    parser = argparse.ArgumentParser(
                        description='''PH Crawler
                            PH 下载器
                        ''')
    parser.add_argument('types',
                        metavar='(hot|av)',
                        help='''要下载的内容类型。
                            hot: 下载热门页面的缩略视频；
                            av: 下载 LIST 文件中指定的视频。
                        ''')
    parser.add_argument('-d', '--dir',
                        metavar = os.getcwd(), default = os.getcwd(),
                        help='''工作目录。
                            phcrawler 会在 工作目录 中下载视频、写入日志以及寻找 ph.list。
                            不指定则默认 当前目录 为 工作目录。
                        ''')
    parser.add_argument('-l', '--list',
                        metavar = join(os.getcwd(),'ph.list'),
                        help='''LIST 文件路径。
                            默认在工作目录下寻找名为的 ph.list 的文件。
                            ph.list 文件格式参考 
                        ''')
    parser.add_argument('-p', '--proxy',
                        metavar = 'http://127.0.0.1:1080', default = os.environ.get('http_proxy'),
                        help='''指定代理服务器地址和端口，以通过代理访问视频网站。
                            目前只支持 HTTP 代理。默认读取环境变量 http_proxy 的值。
                        ''')
    
    args = parser.parse_args()

    if not args.list:
        args.list = join(args.dir, 'ph.list')

    # proxies = {
    #     "http": "socks5://127.0.0.1:1080",
    #     "https": "socks5://127.0.0.1:1080",
    # }
    proxies = {
        'http': args.proxy,
        'https': args.proxy
    }

    # logger.add( "%s.log" % __file__.rstrip('.py'),
    #   format="{time:MM-DD HH:mm:ss} {level} {message}")
    logger.add( join(args.dir, "phcrawler.log"),
        format="{time:MM-DD HH:mm:ss} {level} {message}")

    if proxies:
        logger.info('use proxy -> "%s" for http and "%s" for https' % (proxies['http'], proxies['https']))

    def mk_dir(name):
        path = join(args.dir, name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def processed_keys():
        new_keys = []
        # 也可以三目运算：
        # args.list if args.list else join(args.dir, 'ph.list')
        with open(args.list, 'r') as file:
            for key in list(set(file.readlines())):  # 很遗憾，不能 with list(set(file.readlines())) as keys，无法保证无副作用的情况下又有可读性
                key = key.partition('#')[0]          # 把 # 注释去掉
                key = key.rstrip()
                if not key:
                    continue
                # .strip()
                new_keys.append(key) # 读进来的 key 带换行或空格必须移除
        return new_keys

    if args.types == 'hot':
        # https://www.pornhub.com/categories
        urls = [
            'https://www.pornhub.com/video?o=tr', 'https://www.pornhub.com/video?o=ht',
            'https://www.pornhub.com/video?o=mv', 'https://www.pornhub.com/video'
        ]
        for url in urls:
            info_list = ListPage(url, proxies)
            for info in info_list:
                PHDownload(info['url'], info['key'], 'webm', mk_dir('Preview'), proxies)
    elif args.types == 'av':
        for key in processed_keys():
            if key.find('youtube.com')>=0 or key.find('youtu.be')>=0 :
                url = key
                logger.info('download from -> {}', url)
                TBDownload(url, mk_dir('YouTube'), proxies)
            elif key.find('bilibili.com')>=0 :
                print('b 站白嫖功能还在开发中')
            else:
                url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key
                logger.info('download from -> {}', url)
                info_dict = DetailPage(url, key, proxies)
                for video_url in info_dict['url']:
                    PHDownload(video_url, info_dict['title'], 'mp4', mk_dir('PornHub'), proxies, key)
    else:
        print('unknown content type')
        return
    logger.info('finished !')

if __name__ == '__main__':
    entry()
