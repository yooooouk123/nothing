__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/6/2016'

import re
import os
from datetime import datetime
from newsCrawler3.newsCrawler import NewsCrawler


class ExternalNews(NewsCrawler):
    # represent external news crawler

    def __init__(self):
        NewsCrawler.__init__(self)

    def get_external_news(self, soup, dsc, url, regex_dict):
        for script in soup(["script", "style", "a"]):
            script.extract()
        dsc_replaced = self.multi_replace(regex_dict, dsc)
        try:
            children = soup.findAll(text=re.compile(dsc_replaced)) 		# escape regex characters
            children = [x for x in children if x.parent.name not in ["meta", "title", "link"]]
        except re.error:
                return (2, "dsc not found error")
        # if there's no part matching with dsc (SECOND TRY)
        if len(children) == 0:
            res_code, children = self.search_retry(dsc, dsc_replaced, url, soup, 2)
            if res_code == 2:
                return (res_code, children)      # fail to find dsc
            elif len(children) == 1:
                body = self.get_body(children[0])
            else:
                longest_idx = self.get_longest(children)
                body = self.get_body(children[longest_idx])
        # else if there's the only one part matching with dsc (NICE)
        elif len(children) == 1:
            body = self.get_body(children[0])
        # if there're multiple part matching with dsc (FIND THE LONGEST ONE)
        else:
            longest_idx = self.get_longest(children)
            body = self.get_body(children[longest_idx])
        return (1, body.replace("\n", " "))


    def get_longest(self, children):
        size_list = []
        for child in children:
            try:
                size_list.append(child.parent.parent.get_text(strip=True))
            except AttributeError:
                pass
        longest = max(size_list, key=len)
        longest_idx = size_list.index(longest)
        return longest_idx


    def get_body(self, child):
        parent_tag = child.parent.name
        pre_siblings = child.parent.findPreviousSiblings(parent_tag)
        next_siblings = child.parent.findNextSiblings(parent_tag)
        result = ""
        for s in pre_siblings:
            if s != []:
                result += "\n" + s.get_text()
        try:
            result += "\n" + child.parent.get_text()
        except AttributeError:
            result += "\n" + child.string
        for n in next_siblings:
            if n != [] and n is not None:
                try:
                    result += "\n" + n.get_text()
                except AttributeError:
                    try:
                        result += "\n" + n.string
                    except TypeError:
                        continue
        return result


    def search_retry(self, dsc, dsc_replaced, url, soup, trial):
        children = []
        dsc_len = len(dsc_replaced)-1           # second try
        while True:
            if len(children) != 0:
                break
            elif dsc_len <= 5:
            # write to file errors
                return (2, "dsc not found error")
            try:
                children = soup.findAll(text=re.compile(dsc_replaced[:dsc_len]))
            except:
                pass
            dsc_len -= 1
        return (1, children)


    def multi_replace(self, input_dict, text):
        input_dict = dict((re.escape(k), v) for k, v in input_dict.items())
        pattern = re.compile("|".join(input_dict.keys()))
        replaced = pattern.sub(lambda m: input_dict[re.escape(m.group(0))], text)

        return replaced