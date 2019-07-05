python console.py getNodeVersion
python console.py getPeers
python console.py getBlockNumber
python console.py getBlockByNumber 2
python console.py getBlockByNumber 2 true
python console.py getBlockByHash 0x3654bb69b292cb70cff6d342861a6bc67c6d8ed9f63551dbb3f6f52a41d6aac9 true
python console.py getTransactionByHash 0x281c96b4e1950401129adeb254ce519866a82d724be0e1058efe49996fa8debc SimpleInfo
python console.py getTransactionReceipt  0x281c96b4e1950401129adeb254ce519866a82d724be0e1058efe49996fa8debc SimpleInfo
python console.py newaccount runcase 123456 save
python console.py deploy contracts/SimpleInfo.bin save
python console.py sendtx SimpleInfo last set 'test' 120 0x7029c502b4f824d19bd7921e9cb74ef92392fb1c
python console.py call SimpleInfo last getall
python console.py call SimpleInfo last getbalance1 111
