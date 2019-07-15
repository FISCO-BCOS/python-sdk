

class BcosError(Exception):
    code = None
    data = None
    message = None
    def __init__(self, code,data,msg):
        self.code = code
        self.data = data
        self.message = msg
    def info(self):
        return "code :{},data :{},message : {}".format(self.code, self.data, self.message)