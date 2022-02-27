from typing import List, Dict, Union
import re


class Pin:
    def __init__(self, site):
        self.site = site

    def ignore_error(default=''):
        """ It avoids any exception, setting a default value if it happens """
        def _decorator(func):
            def wrapper_data(self):
                try:
                    return func(self)
                except Exception:
                    return default
            return wrapper_data
        return _decorator

    @ignore_error()
    def title(self) -> str:
        """ Return pin's title """
        return self.site.html_soup(self.site.ELEMENT_TITLE).h1.string

    @ignore_error()
    def subtitle(self) -> str:
        """ Return pin's subtitle"""
        return self.site.html_soup(self.site.ELEMENT_SUBTITLE).span.string

    @ignore_error([])
    def images(self) -> Union[List[str], list]:
        """ Return pin's images """
        img_soup = self.site.html_soup(self.site.ELEMENT_IMAGES)

        # Single SRC image
        if img_soup.find('img'):
            return [img_soup.find('img').get('src')]

        # Multiple STYLE images
        return list(set([
            url[0]
            for div in img_soup.find_all('div')
            for url in [re.search(
                '(http.?://i.pinimg.com/[0-9]{3}x/../../../[a-z0-9]+\.(?:png|jpg|jpeg))',
                str(div)
                )]
            if url
        ]))


class PinData(Pin):
    def __init__(self, site):
        super().__init__(site)
        self._data = {
            'title': self.title(),
            'subtitle': self.subtitle(),
            'images': self.images()
        }

    @property
    def data(self) -> Dict[str, Union[str, list]]:
        if not self.is_valid():
            return {}
        return self._data

    def is_valid(self, patch=True):
        """ Return whether the data is valid """
        if not self._data['images']:
            return False

        if not self._data['title'] or not self._data['subtitle']:
            if patch:
                self.patch_data()

        return True

    def patch_data(self):
        """ Perform the patching on the data """
        if not self._data['title']:
            self._data['title'] = self._data['subtitle']

        elif not self._data['subtitle']:
            self._data['subtitle'] = self._data['title']
