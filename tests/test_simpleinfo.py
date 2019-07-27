from contracts.SimpleInfo import SimpleInfo

address = "0xf74c2c7131c2461db2e67362a8e7fca6dc0a66bf"
si = SimpleInfo(address)
(outputresult , receipt) = si.set("testeraaa",888,'0x7029c502b4f824d19bd7921e9cb74ef92392fb1F')
logresult = si.data_parser.parse_event_logs(receipt["logs"])
#outputresult  = si.data_parser.parse_receipt_output("set", receipt['output'])
print("receipt output :",outputresult)
i = 0
for log in logresult:
    if 'eventname' in log:
        i = i + 1
        print("{}): log name: {} , data: {}".format(i,log['eventname'],log['eventdata']))
print(si.getall())
print(si.getbalance1(100))