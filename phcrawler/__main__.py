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
    parser_top = argparse.ArgumentParser(
                        description='''PH Crawler PH 下载器
                        ''', add_help=False)
    parser_top.add_argument('-t', '--type',
                        metavar='(video|audio)',
                        help='''要下载的内容类型。
                            video: 下载 LIST 文件中指定的视频。
                            audio: 下载 LIST 文件中指定的音频（不可用）。
                        ''')
    parser_top.add_argument('-d', '--dir',
                        metavar = os.getcwd(), default = os.getcwd(),
                        help='''工作目录。
                            phcrawler 会在 工作目录 中下载视频、写入日志以及寻找 ph.list。
                            不指定则默认 当前目录 为 工作目录。
                        ''')
    parser_top.add_argument('-p', '--proxy',
                        metavar = 'http://127.0.0.1:1080', default = os.environ.get('http_proxy'),
                        help='''指定代理服务器地址和端口，以通过代理访问视频网站。
                            目前只支持 HTTP 代理。默认读取环境变量 http_proxy 的值。
                        ''')
    parser_top.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.2')


    parser = argparse.ArgumentParser(parents=[parser_top], add_help=True)
    parser.add_argument('-l', '--list',
                    metavar = join(os.getcwd(),'ph.list'),
                    help='''LIST 文件（包含路径）。
                        默认在工作目录下寻找名为的 ph.list 的文件。
                        ph.list 文件格式参考 https://github.com/madobet/phcrawler/blob/master/ph.list
                    ''')

    # 注：每个解析器只能有一个 subparsers ，但 subparsers 可以挂载多个 parser
    subparsers = parser.add_subparsers(metavar = 'COMMAND', help='使用 phcrawler COMMAND -h 或 phcrawler COMMAND --help 查看对应的 COMMAND 子命令的帮助')

    # ph 子命令
    parser_ph = subparsers.add_parser('ph', help='ph 子命令。PornHub 视频相关')
    parser_ph.add_argument('--hot', default=False, action='store_true', help='下载热门视频信息')
    parser_ph.add_argument('-c', '--category', metavar='CATEGORY', help='抓取指定分类的视频信息写入 LIST 文件，并下载预览')
    parser_ph.add_argument('-s', '--search', metavar='KEYWORD', help='抓取指定关键字的视频信息写入 LIST 文件，并下载预览')
    parser_ph.add_argument('-r', '--ranges', nargs=2, type=int, metavar=('N1','N2'), help='抓取 N1 页到 N2 页的内容。默认只抓取第一页内容')

    # 只有一个全局参数，没有这种用法: args_ph = parser_ph.parse_args()
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
        # os.mkdir 只能创建一个目录
        # os.makedirs 可以递归创建目录
        if not os.path.exists(path := join(args.dir, name)):
            os.makedirs(path)
        return path

    def processed_keys():
        new_keys = []
        with open(args.list, 'r') as file:
            for key in list(set(file.readlines())):  # 很遗憾，不能 with list(set(file.readlines())) as keys，无法保证无副作用的情况下又有可读性
                if not (key := key.partition('#')[0].rstrip()) : # 把 # 注释和空白去掉
                    continue
                new_keys.append(key) # 读进来的 key 带换行或空格必须移除
        return new_keys

    def bulk_download(folder_name):
        for url in urls:
            # ! 坑: list(range(1,2)) 只返回 [1]，list(range(1,3)) 才返回 [1 2]
            for page in range(args.ranges[0], args.ranges[1]+1) if args.ranges else [1]:
                url += '&page=%s' % page
                logger.info('download following content at %s page from -> {}' % page, url)
                info_list = ListPage(url, file='', proxies=proxies)
                for info in info_list:
                    PHDownload(info['url'], info['title'], 'webm', mk_dir(folder_name), proxies, info['key'])
    # 不知道怎么解决主命令 required 结果子命令也必须指定的问题…… argparse 这东西真的难用
    if args.type == 'video':
        for key in processed_keys():
            if key.find('youtube.com')>=0 or key.find('youtu.be')>=0 :
                url = key
                key = url.split('?')[-1]
                logger.info('download from YouTube -> {}', url)
                TBDownload(url, mk_dir('YouTube'), key, proxies)
            elif key.find('bilibili.com')>=0 :
                print('download from BiliBili ->')
            elif key.find('pornhub.com')>=0 :
                url = key
                key = url.split('viewkey=')[-1]
                logger.info('download from PornHub -> {}', url)
                info_dict = DetailPage(url, key, proxies)
                for video_url in info_dict['url']:
                    PHDownload(video_url, info_dict['title'], 'mp4', mk_dir('PornHub'), proxies, key)
            else:
                url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key
                logger.info('download from PornHub -> {}', url)
                info_dict = DetailPage(url, key, proxies)
                for video_url in info_dict['url']:
                    PHDownload(video_url, info_dict['title'], 'mp4', mk_dir('PornHub'), proxies, key)
    elif args.hot:
        urls = [
            'https://www.pornhub.com/video?o=tr',
            'https://www.pornhub.com/video?o=ht',
            'https://www.pornhub.com/video?o=mv',
            'https://www.pornhub.com/video'
        ]
        bulk_download( 'Hot' )
    elif args.category:
        urls = [ 'https://www.pornhub.com/categories/%s' % args.category ]
        bulk_download( join('Category', args.category) )
    elif args.search:
        urls = [ 'https://www.pornhub.com/video/search?search=%s' % args.search ]
        bulk_download( join('Search', args.search) )
    else:
        return
    logger.info('finished !')

if __name__ == '__main__':
    entry()
