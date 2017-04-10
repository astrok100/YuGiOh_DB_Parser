from lxml import etree
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlParserLinkExtractor, _nons, _collect_string_content 
from scrapy.utils.misc import arg_to_iter, rel_has_nofollow
from scrapy.utils.python import unique as unique_list, to_native_str
from six.moves.urllib.parse import urljoin
from scrapy.utils.response import get_base_url

class YuGiOhParserLink(LxmlParserLinkExtractor):
    def __init__(self, tag="a", attr="href", process=None, unique=False):
        super(YuGiOhParserLink, self).__init__(
            tag=tag, attr=attr, process=process, unique=unique
        )

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = []
        # hacky way to get the underlying lxml parsed document
        for el, attr, attr_val in self._iter_links(selector.root):
            # pseudo lxml.html.HtmlElement.make_links_absolute(base_url)
            try:
                attr_val = urljoin(base_url, attr_val)

            except ValueError:
                continue # skipping bogus links
            else:
                url = self.process_attr(attr_val, el.attrib)
                if url is None:
                    continue
            url = to_native_str(url, encoding=response_encoding)
            # to fix relative links after process_value
            url = urljoin(response_url, url)
            link = Link(url, _collect_string_content(el) or u'',
                        nofollow=rel_has_nofollow(el.get('rel')))

            links.append(link)
        return self._deduplicate_if_needed(links)


class YuGiOhLinkExtractor(LinkExtractor):
    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(),
                 tags=('a', 'area'), attrs=('href',), canonicalize=True,
                 unique=True, process_value=None, deny_extensions=None, restrict_css=()):
        self.tags = tags
        self.attrs = attrs
        tag_func = lambda x: x in set(arg_to_iter(self.tags))
        attr_func = lambda x: x in set(arg_to_iter(self.attrs))

        super(YuGiOhLinkExtractor, self).__init__(
            allow=allow, deny=deny,
            allow_domains=allow_domains, deny_domains=deny_domains,
            restrict_xpaths=restrict_xpaths, restrict_css=restrict_css,
            canonicalize=canonicalize, deny_extensions=deny_extensions
        )

        self.link_extractor = YuGiOhParserLink(
            tag=tag_func, attr=attr_func,
            unique=unique,
            process=process_value
        )


    def extract_links(self, response):
        base_url = get_base_url(response)
        if self.restrict_xpaths:
            docs = [subdoc
                    for x in self.restrict_xpaths
                    for subdoc in response.xpath(x)]
        else:
            docs = [response.selector]
        all_links = []
        for doc in docs:
            doc.root.attrib['text_content'] = doc.root.text_content()
            links = self._extract_links(doc, response.url, response.encoding, base_url)
            all_links.extend(self._process_links(links))
        return unique_list(all_links)
