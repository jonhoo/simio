all: simulator/chan.py renderer/bin/renderer

simulator/chan.py: parser/chan.ioa parser/parser.py
	parser/parser.py -f $< > $@

renderer/bin/renderer: renderer/src/renderer/renderer.go
	(cd renderer; GOPATH="$(shell "pwd")/renderer" go get renderer/...)
