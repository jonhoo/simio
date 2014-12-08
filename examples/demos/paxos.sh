#!/bin/bash
base="$(dirname "$(readlink -f "$0")")/../.."
"$base/src/parser/parser.py" -f "$base/examples/specs/paxos.ioa" > wtf.py
"$base/src/simulator/simulator.py" "$@" -g "$base/examples/graphs/complete.gv"
rm wtf.py
