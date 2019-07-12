

class BcosError(Exception):
    code = None
    data = None
    message = None
    def __init__(self, c,d,m):
        self.code = c
        self.data = d
        self.message = m
    def info(self):
        return "code :{},data :{},message : {}".format(self.code, self.data, self.message)