import os
import sys
import argparse
import unicodedata
import re
import pprint
import getpass

from PyQt5.QtCore import *

DEFAULT_DATA_PATH = 'C:\\Users\\{$USER}\\AppData\\Roaming\\qBittorrent'
STORAGE_FILENAME = 'qBittorrent.ini'
CATEGORIES_KEY = 'BitTorrent/Session/Categories'
KEY_PATH_SEPARATOR = '-'


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


class Generator():
    def run(self, cmdargs):
        parser = argparse.ArgumentParser(
            prog="%s" % sys.argv[0].split(os.path.sep)[-1],
            description=self.__doc__
        )
        parser.add_argument(
            '--data-path',
            dest='data_path',
            default=DEFAULT_DATA_PATH,
            help='path where qBittorrent conf file is located'
        )
        parser.add_argument(
            '--base-path',
            dest='base_path',
            help='base path used to auto-generate categories',
            required=True
        )
        parser.add_argument(
            '--ignorelist-path',
            dest='ignorelist_path',
            help='path to a python file containing list of path '
            'to ignore when parsing base path content'
        )
        parser.add_argument(
            '--cleanlist-path',
            dest='cleanlist_path',
            help='path to a python file containing a list of string '
            'that will be removed from the categry name'
        )
        parser.add_argument(
            '--remove-dir',
            dest='remove_dir',
            action='store_true',
            help='remove category with non-existing path'
        )
        parser.add_argument(
            '--use-subcategories',
            dest='use_subcategories',
            action='store_true',
            help='keep path separator to comply with subcategories mode'
        )
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            help='do not save results'
        )

        if not cmdargs:
            sys.exit(parser.print_help())

        self.args = parser.parse_args(args=cmdargs)

        if self.args.ignorelist_path and os.path.exists(
            self.args.ignorelist_path
        ):
            content = open(self.args.ignorelist_path, 'r').read()
            self.ignorelist = eval(content)
        else:
            self.ignorelist = []

        if self.args.cleanlist_path and os.path.exists(
            self.args.cleanlist_path
        ):
            content = open(self.args.cleanlist_path, 'r').read()
            self.cleanlist = eval(content)
        else:
            self.cleanlist = []

        # Read existing categories from ini/conf file
        storage_path = STORAGE_FILENAME
        if self.args.data_path:
            # Replace username if default path
            self.args.data_path = self.args.data_path.replace(
                '{$USER}', getpass.getuser()
            )
            if os.path.exists(self.args.data_path):
                storage_path = os.path.join(self.args.data_path, storage_path)

        # Try to load data from given path
        if os.path.exists(self.args.data_path):
            print('Loading', storage_path)
            settings = QSettings(storage_path, QSettings.IniFormat)
            self.categories = settings.value(CATEGORIES_KEY)
            if self.categories is None:
                self.categories = {}
            print('categories', '=', pprint.pformat(self.categories))
        else:
            raise Exception("Invalid --data-path: %s" % self.args.data_path)

        # Remove category with non existing path
        if self.args.remove_dir:
            updated_categories = {}
            for key, path in self.categories.items():
                if os.path.exists(path):
                    updated_categories[key] = path
                else:
                    print('Removing', key, '=', path)
            if updated_categories:
                self.categories = updated_categories

        # Update categories from path data
        self.update_with(self.args.base_path)

        # Save new categories value
        if not self.args.dry_run:
            settings.setValue(CATEGORIES_KEY, self.categories)
        else:
            print(self.categories)

    def update_with(self, path):
        key = self.clean_path_key(path)
        # Check that a full episode name is not in the folder name
        # eg: "TVShow.S02E13.MULTi.1080p.x264" will be ignored
        m = re.search('[sS]\d\d[eE]\d\d', key)
        if not m:
            # Store and convert path with unix separator to comply
            # with QBittorrent default format
            if key not in self.ignorelist:
                self.categories[key] = path.replace(os.sep, '/')
                print(key, '=', path)
            for item in os.listdir(path):
                fullpath = os.path.join(path, item)
                if os.path.isdir(fullpath):
                    self.update_with(fullpath)

    def clean_path_key(self, key):
        res = remove_accents(key)
        # Remove path separator if not enabled in QBittorrent
        if not self.args.use_subcategories:
            res = res.replace(os.sep, KEY_PATH_SEPARATOR)
        # Remove dot separator
        res = res.replace('.', '')
        # Remove drive letter
        if ':' in res:
            res = res.split(':')
            res = res[1]
        # Apply cleaning from user given list
        for item in self.cleanlist:
            res = res.replace(item, '')
        if self.args.use_subcategories:
            res = res.strip(os.sep)
            res = res.replace(os.sep, '/')
        else:
            res = res.strip(KEY_PATH_SEPARATOR)
        return res


if __name__ == '__main__':
    Generator().run(sys.argv[1:])