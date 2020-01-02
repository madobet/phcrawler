import fire
import phcrawler

def main():
  # - 目前用 fire 自动生成文档，但如果使用 argparse 标准库处理参数：
  # parser = argparse.ArgumentParser(description='PH Crawler')
  # parser.add_argument('type', metavar='(webm|mp4)', help='要下载的内容类型。指定 webm 下载热门页面的缩略图；指定 mp4 下载工作目录中 phlist.txt 文件指定的视频')
  # parser.add_argument('-d', '--dir', default = os.getcwd() + '/' ,help='视频保存目录，默认当前工作目录')
  # parser.add_argument('-p', '--proxy', help='指定代理地址，只支持 HTTP 代理 (如 http://127.0.0.1:1080)')
  #
  # args = parser.parse_args()
  #
  # if args.proxy:
  #   proxies['http'] = args.proxy
  #   proxies['https'] = args.proxy
  # else:
  #   proxies.clear
  #
  # run()

  # 代码参考 https://github.com/formateddd/pornhub
  fire.Fire(phcrawler.Run)

if __name__ == '__main__':
  main()
