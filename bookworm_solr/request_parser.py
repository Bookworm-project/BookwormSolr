import logging
import json
from urllib import urlencode

class RequestParser:
    FUNCS = ['or', 'and', 'gte', 'gt', 'lte', 'lt', 'ne', 'eq']

    def __init__(self, base):
        self.base = base if base[-1] != "/" else base[:-1]
        logging.info("Starting Bookworm=>Solr Request Parser for {0}".format(base))

    def query(self, q):
        ''' Take a Bookworm API query and return a Solr curl request '''
        logging.debug("Parsing to JSON")
        jsonq = json.loads(q)
        url ={}

        if 'search_limits' in jsonq:
            logging.debug("Parsing search limits")
            url['q'] = self._parse_node('$limit', jsonq['search_limits'])

        if 'compare_limits' in jsonq:
            logging.debug("Parsing compare limits")
        
        return self.base+"/select?"+urlencode(url)

    def _parse_node(self, key, value, joiner=" AND ", field=None):
        field = key if field is None else field
        if key == '$limit':
            subq = joiner.join(self._parse_node(k, v, field=k) for k,v in value.iteritems())
            return subq
        elif key[0] == '$':
            func = key[1:].lower()
            if func in self.FUNCS:
                call = getattr(self, "_"+func)
                return call(field, value)
            else:
                logging.error("Unrecognized function {}".format(key))
        else:
            if type(value) is list or type(value) is str or type(value) is unicode:
                # Simple style
                subq = self._eq(key, value)
            elif type(value) is dict:
                subq = joiner.join(self._parse_node(k, v, field=field) for k,v in value.iteritems())
            return subq
            
    def _eq(self, field, q):
        logging.debug("$eq {0}".format(q))
        if type(q) is int:
            subq = q
        elif type(q) is str or type(q) is unicode:
            subq = q
        elif type(q) is list:
            subq = " OR ".join([str(v) for v in q])
            subq ="({0})".format(subq)

        return "+{0}:{1}".format(field, subq)


    def _or(self, field, q, joiner=" OR "):
        field = "$limit" if field.lower() == "$or" else field
        l = ["(%s)" % self._parse_node(field, item) for item in q]
        return "(%s)" % " OR ".join(l)

    def _and(self, field, q):
        field = "$limit" if field.lower() == "$and" else field
        return self._or(field, q)
        

    def _ne(self, field, q):
        logging.debug("$ne {0}".format(q))
        eq = self._eq(field, q)
        return '-'+eq[1:]
        

    def _gte(self, field, q):
        return "+{0}:[{1} TO *]".format(field, q)

    def _gt(self, field, q):
        return "+{0}:[{1} TO *]".format(field, q+1)

    def _lte(self, field, q):
        return "+{0}:[* TO {1}]".format(field, q)

    def _lt(self, field, q):
        return "+{0}:[* TO {1}]".format(field, q+1)
