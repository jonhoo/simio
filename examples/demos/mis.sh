#!/bin/bash
base="$(dirname "$(readlink -f "$0")")/../.."
"$base/src/parser/parser.py" -f "$base/examples/specs/luby-mis.ioa" > wtf.py
"$base/src/simulator/simulator.py" "$@" -g "$base/examples/graphs/arbitrary.gv"
rm wtf.py
