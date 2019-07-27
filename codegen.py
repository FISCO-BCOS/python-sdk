import sys
from client.bcosclient import BcosClient
from client.datatype_parser import  DatatypeParser
from utils.abi import  (
	filter_by_type, #通过类型选择一组元素，如"function","event"等
	)
import os


class ABICodegen:
    parser = DatatypeParser()
    abi_file = ""
    name = ""
    indent = "    "
    def __init__(self,abi_file):
        if len(abi_file) > 0:
            self.load_abi(abi_file)
    def load_abi(self,abi_file):
        self.abi_file = abi_file
        self.parser.load_abi_file(abi_file)
        fname = os.path.basename(abi_file)
        (self.name, ext) = os.path.splitext(fname)



    def make_function(self,func_abi):
        func_lines =[]
        func_def ="def {}( self".format( func_abi["name"] )
        args_def = ""
        args_value = ""
        i = 0
        for param in func_abi["inputs"]:
            if i> 0:
                args_def+=" , "
                args_value +=" , "
            args_def += param["name"]
            if param['type'] =="address":
                args_value += "to_checksum_address({})".format(param["name"])
            else:
                args_value += param["name"]
            i+=1
        if len(args_def) > 0:
            func_def += " , "+args_def
        func_def+= " ):"
        func_lines.append(func_def)
        func_lines.append("{}func_name='{}'".format(self.indent,func_abi["name"]))
        func_lines.append("{}args=[{}]".format(self.indent, args_value))
        if func_abi["constant"] is False:
            func_lines.append(self.indent+"receipt = self.client.sendRawTransactionGetReceipt(self.address,self.contract_abi,func_name,args)")
            if "outputs" in func_abi:
                func_lines.append(self.indent+"outputresult  = self.data_parser.parse_receipt_output(func_name, receipt['output'])")
                func_lines.append(self.indent+"return (outputresult,receipt)")
            else:
                func_lines.append(self.indent + "return (receipt)")
        if func_abi["constant"] is True:
            func_lines.append(self.indent+"result = self.client.call(self.address,self.contract_abi,func_name,args)")
            func_lines.append(self.indent+"return result")

        return func_lines


    def gen_all(self):
        all_func_code_line  = []
        func_abi_list = filter_by_type("function", self.parser.contract_abi)
        for func_abi in func_abi_list:
            func_lines = self.make_function(func_abi)
            all_func_code_line.append("#------------------------------------------")
            all_func_code_line.extend(func_lines)
            print(func_lines)
        template='''
from client.bcosclient import (
     BcosClient,
     BcosError
)
import os
from eth_utils import to_checksum_address
from client.datatype_parser import DatatypeParser

class {}: #name of abi
    address =None
    abi_file  ="{}" #abi file in path
    contract_abi =""
    data_parser = DatatypeParser()
    client = BcosClient()
    def __init__(self,address):
        self.address= address
        self.data_parser.load_abi_file(self.abi_file)
        self.contract_abi = self.data_parser.contract_abi
'''.format(self.name,self.abi_file)
        for line in all_func_code_line:
            template += self.indent+line+"\n"
        return template


def usage():
    usagetext = '''usage: 
    python codegen.py [abifile(eg: ./contracts/SimpleInfo.abi)] [outputpath(eg: ./contracts/)] '''
    print(usagetext)
if __name__ == '__main__':
    #print (sys.argv)
    if(len(sys.argv)<3):
        usage()
        sys.exit(0)
    abi_file = sys.argv[1]
    outputdir = sys.argv[2]
    forcewrite = False
    if(len(sys.argv)==4):
        isSave = sys.argv[3]
        if isSave=="save":
            forcewrite = True
    codegen = ABICodegen(abi_file)
    template = codegen.gen_all()
    print(template)
    name = codegen.name+'.py'
    outputfile = os.path.join(outputdir, name)
    print(" output file : {}".format(outputfile))

    if os.access(outputfile, os.F_OK) and forcewrite is False:
        str = input(">> file [{}] exist , continue (y/n): ".format(outputfile));
        if (str.lower() == "y"):
            forcewrite = True
        else:
            forcewrite = False
    else:
        forcewrite = True
    if forcewrite:
        with open(outputfile,"wb") as f:
            f.write(bytes(template,"utf-8") )
            f.close()
        print("write {} done".format(outputfile))


