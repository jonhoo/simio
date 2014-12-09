#!/bin/bash
base="$(dirname "$(readlink -f "$0")")/../.."
"$base/src/parser/parser.py" -f "$base/examples/specs/abelian.ioa" > wtf.py
"$base/src/simulator/simulator.py" "$@" -g "$base/examples/graphs/bellman-ford.gv"
rm wtf.py
