#!/bin/bash
base="$(dirname "$(readlink -f "$0")")/../.."
"$base/src/parser/parser.py" -f "$base/examples/specs/peterson.ioa" > wtf.py
"$base/src/simulator/simulator.py" "$@" -g "$base/examples/graphs/ring.gv"
rm wtf.py
