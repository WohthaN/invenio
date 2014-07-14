class DataDict(object):

    def sanitize(self, li):
        return [x for x in li if x]


class NotExistent(Exception):
    pass
