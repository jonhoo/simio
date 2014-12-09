simio is an [I/O
Automata](http://groups.csail.mit.edu/tds/papers/Lynch/ioa-leavens.pdf)
simulator, that aims to provide students of distributed systems with tools for
visualizing the behaviour of I/O automata in arbitrary networks.

To use the tool, first run `make`.

Next, the simulator expects definitions of automata to be written using a thin
Domain-Specific Language that wraps Python. Examples implementations of common
distributed algorithms can be seen in [examples/specs](examples/specs/). The
simio parser, `src/parser/parser.py`, should then be invoked on the automaton
specification to generate an executable automaton file:

    # Note that the output file *must* currently be called wtf.py
    ./src/parser/parser.py -f examples/specs/paxos.ioa > wtf.py

Next, a network graph should be defined using the Graphviz [DOT
format](http://www.graphviz.org/content/dot-language). All edges represent a
FIFO channel, and all nodes in the graph will be running a single instance of
the automaton. Example graphs can be seen in
[examples/graphs](examples/graphs/). Now, the simulator can be invoked by
running:

    ./src/simulator/simulator.py -s .2 -g examples/graphs/complete.gv

This will open up a live view of the simulation in a new window, powered by the
simio [renderer](src/renderer/src/renderer/). The `-s` option specifies the
time delay between each step of the simulation, and allows speeding up or
slowing down the visualization.

The simulator's `STDOUT` will contain anything printed inside the running
automaton instances, while `STDERR` will contain messages from the simulator.

## Quick demos

To see quick demos, run `make`, and then run one of the scripts in the
[examples/demos](examples/demos) directory. Demos for Bellman-Ford, Paxos,
Peterson's leader-election algorithm, and Luby Maximal Independent Set are
given.
