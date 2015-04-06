#!/usr/bin/env python
# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from bs4 import BeautifulSoup
import fnmatch
import argparse
import os.path
import pickledb
import csv


def load_translation(inputfile):
    """
    Google Docs에서 export 된 CSV 파일을 메로리로 로드.
    """
    db = pickledb.load('trans.db', False)
    if not os.path.isfile('trans.db'):
        with open(inputfile, 'r') as translation_input:
            reader = csv.DictReader(translation_input)
            for row in reader:
                db.set(row['Input'], row['Translation'])
            db.dump()
    return db


def patch_translation(html_doc, target_dict):
    """
    파일 하나씩 돌면서, HTML 태그를 제외한 스트링을 target_dict에 있는
    키와 대조 및 바꿈.
    """
    soup = BeautifulSoup(html_doc)
    for t in soup.findAll(text=True):
        text = unicode(t.strip())
        translation = target_dict.get(text)
        if translation is not None:
            t.replaceWith(translation)
    return soup.prettify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='번역 데이터를 다시 프론트엔드로 패치.')
    parser.add_argument('directory', help='프론트엔드 코드.')
    args = parser.parse_args()

    excludes = [
        'out',
        'bower_components',
        'app',
        'node_modules',
    ]

    root_dir = args.directory
    if root_dir[-1:] != '/':
        root_dir += '/'

    excludes = [root_dir+abs_dir for abs_dir in excludes]

    files = []
    for root, dirnames, filenames in os.walk(args.directory, topdown=True):
        skip = False
        for exclude_dir in excludes:
            if root.startswith(exclude_dir):
                print 'Excluding ' + root
                skip = True
        if not skip:
            for filename in fnmatch.filter(filenames, '*.html'):
                files.append(os.path.join(root, filename))

    trans_dict = load_translation('input.csv')

    for viewfile in files:
        print 'Processing ' + viewfile
        with open(viewfile, 'r+') as f:
            patched_text = patch_translation(f, trans_dict)
            f.seek(0)
            f.write(patched_text.encode('utf8'))
            f.truncate()
