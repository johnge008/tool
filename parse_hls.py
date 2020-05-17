# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:john
@file: parse_hls.py
@time: 2020/05/17
"""

import m3u8
import requests
import os
from optparse import OptionParser


class HlsDownload(object):
    def __init__(self, url: str, path: str, ua: str):
        self.url = url
        self.path = path
        self.ua = ua

    def start(self):
        # only support one sub m3u8.
        m = m3u8.load(self.url)
        if len(m.playlists) == 0:
            self.__download_playlist(m, 'index.m3u8')
        else:
            self.__save_to_file('index.m3u8', m.dumps(), 'w')
            for pl in m.playlists:
                m2 = m3u8.load(pl.absolute_uri)
                self.__download_playlist(m2, pl.uri)

    def __download_playlist(self, playlist, file_name: str):
        print('start download: ' + playlist.base_uri)
        self.__save_to_file(file_name, playlist.dumps(), 'w')
        for sm in playlist.segments:
            print('segment: ' + sm.absolute_uri)
            content = self.__download_segment(sm.absolute_uri)
            if content is not None:
                sm_path = os.path.join(os.path.dirname(file_name), sm.uri)
                self.__save_to_file(sm_path, content, 'wb')

    def __download_segment(self, segment_url: str):
        headers = {'User-Agent': self.ua}
        res = requests.get(segment_url, headers)
        if res.status_code != 200:
            print('download url:' + segment_url + 'error: ' + res.status_code)
            return None
        else:
            return res.content

    def __save_to_file(self, file_name: str, content, mode: str):
        absolute_path = os.path.join(os.path.abspath(self.path),
                                     os.path.dirname(file_name))
        is_exist = os.path.exists(absolute_path)
        if not is_exist:
            os.makedirs(absolute_path, 0o777)
        absolute_file_path = os.path.join(absolute_path, os.path.basename(
            file_name))
        with open(absolute_file_path, mode) as f:
            f.write(content)


if __name__ == '__main__':
    '''
    http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8
    http://devimages.apple.com/iphone/samples/bipbop/gear1/prog_index.m3u8
    '''
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", help="url of m3u8")
    parser.add_option("-A", "--user-agent", dest="ua",
                      default='Mozilla/5.0 (X11; Linux x86_64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/81.0.4044.113 Safari/537.36',
                      help="user-agent for download")
    parser.add_option("-p", "--path", dest="path", default='download',
                      help="download folder")
    (options, args) = parser.parse_args()

    if not os.path.isabs(options.path):
        options.path = os.path.join(os.path.abspath('./'), options.path)

    hls_download = HlsDownload(options.url, options.path, options.ua)
    hls_download.start()
    print('download folder: ' + options.path)
