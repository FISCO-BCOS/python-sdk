.SUFFIX: .sol .bin .abi
SOLC=$(HOME)/.py-solc/solc-v0.4.25/bin/solc
CFLAGS=--bin --abi --overwrite
ODIR=-o .
#ODIR=-o . --overwrite


%.bin: %.sol
	$(SOLC) $(CFLAGS) $< $(ODIR)

#all: DemoInnerMapping.bin
