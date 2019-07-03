python console.py getNodeVersion
python console.py getPeers
python console.py getBlockNumber
python console.py getBlockByNumber 2
python console.py getBlockByNumber 2 true
python console.py getBlockByHash 0x594148f7a4e53a0def1ca378fec22d85abedb0b550d5d290c84c951e77be6d7c true
python console.py getTransactionByHash 0x994bab93f776c7ed79f01bd026e71124276b58446139715f915ad9c1ce6bda4d SimpleInfo
python console.py getTransactionReceipt  0x994bab93f776c7ed79f01bd026e71124276b58446139715f915ad9c1ce6bda4d SimpleInfo
python console.py newaccount runcase 123456 save
python console.py deploy sample/SimpleInfo.bin
python console.py sendtx SimpleInfo last set 'test' 120 0x7029c502b4f824d19bd7921e9cb74ef92392fb1c
python console.py call SimpleInfo last getall
python console.py call SimpleInfo last getbalance1 111
