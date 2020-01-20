.SUFFIX: .sol .bin .abi

CONSOLE=./console.py
DFLAG=save
OBJ=HelloWorld
BIN=$(OBJ:=.bin)
INPUT=0x1234

# Variables defined to create or show account
ACCNT=denpus
PASSWD=123456
NAFLAG=save

#call or sendtx
ADDR=0xf68f1ba403162959bf61f014c2ed57c7868b604a
CALLF=get
SENDF=set
ARGS="Hello World! How are you?"

#getBlockHashByNumber
BLKNO=196
TRANHASH=0x01
CONADDR=0x02
BLKHASH=0x015d3c87b00bb116781722e7ff8e46d600d8d994d2655ce7f6db0ea42a626fc6

#Permission
TBLNM=t_demo

install:
    @
usage:
	@$(CONSOLE) $@
	
newaccount:
	@$(CONSOLE) $@ $(ACCNT) $(PASSWD) 
showaccount:
	@$(CONSOLE) $@ $(ACCNT) $(PASSWD)
	
compile: 
	@cd contracts && make $(BIN)
deploy: 
	@$(CONSOLE) $@ $(OBJ) $(DFLAG)

call:
	@$(CONSOLE) $@ $(OBJ) $(ADDR) $(CALLF) $(ARGS)
sendtx:
	@$(CONSOLE) $@ $(OBJ) $(ADDR) $(SENDF) $(ARGS)
	
blkno:
	@$(CONSOLE) getBlockNumber
peers:
	@$(CONSOLE) getPeers
nodever:
	@$(CONSOLE) getNodeVersion
pbftview:
	@$(CONSOLE) getPbftView
sealers:
	@$(CONSOLE) getSealerList
observers:
	@$(CONSOLE) getObserverList
consens:
	@$(CONSOLE) getConsensusStatus
syncs:
	@$(CONSOLE) getSyncStatus
groupeers:
	@$(CONSOLE) getGroupPeers
nodelist:
	@$(CONSOLE) getNodeIDList
grouplist:
	@$(CONSOLE) getGroupList
pendtxsize:
	@$(CONSOLE) getPendingTxSize
transcount:
	@$(CONSOLE) getTotalTransactionCount
pendtrans:
	@$(CONSOLE) getPendingTransactions
blockhash:
	@$(CONSOLE) getBlockHashByNumber $(BLKNO)
tranbyhash:
	@$(CONSOLE) getTransactionByHash $(TRANHASH) $(OBJ)
tranrec:
	@$(CONSOLE) getTransactionReceipt $(TRANHASH) $(OBJ)
bincode:
	@$(CONSOLE) getCode $(CONADDR)
tranbybhi:
	@$(CONSOLE) getTransactionByBlockHashAndIndex $(BLKHASH) $(TRANIDX) $(OBJ)
tranbybni:
	@$(CONSOLE) getTransactionByBlockNumberAndIndex $(BLKNO) $(TRANIDX) $(OBJ)
tx_count_limit:
	@$(CONSOLE) getSystemConfigByKey $@
tx_gas_limit:
	@$(CONSOLE) getSystemConfigByKey $@
blkbynot:
	@$(CONSOLE) getBlockByNumber $(BLKNO) True
blkbynof:
	@$(CONSOLE) getBlockByNumber $(BLKNO) False
blkbyhasht:
	@$(CONSOLE) getBlockByHash $(BLKHASH) True
blkbyhashf:
	@$(CONSOLE) getBlockByHash $(BLKHASH) False
blklatest:
	@$(eval BLKLATEST:=$(shell $(CONSOLE) getBlockNumber|tail -1| sed -e 's/[> ]*//g'))
	$(CONSOLE) getBlockByNumber $(BLKLATEST)

listutm:
	@$(CONSOLE) listUserTableManager $(TBLNM) 
listdcm:
	@$(CONSOLE) listDeployAndCreateManager 
listpm:
	@$(CONSOLE) listPermissionManager
listnm:
	@$(CONSOLE) listNodeManager
listscm:
	@$(CONSOLE) listSysConfigManager
listcnsm:
	@$(CONSOLE) listCNSManager

txinput:
	@$(CONSOLE) $@ $(OBJ) $(INPUT)		
txinputlatest:
	@$(eval BLKLATEST:=$(shell $(CONSOLE) getBlockNumber|tail -1| sed -e 's/[> ]*//g'))
	@$(eval INPUTLATEST:=$(shell $(CONSOLE) getBlockByNumber $(BLKLATEST)| grep "input"|awk -F":" '{print $2}'))
	@make INPUT=$(INPUTLATEST) txinput
