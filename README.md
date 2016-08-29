simio is an [I/O Automata](http://groups.csail.mit.edu/tds/papers/Lynch/ioa-leavens.pdf)
simulator, that aims to provide students of distributed systems with
tools for visualizing the behaviour of I/O automata in arbitrary
networks.

To build the toolkit, run `make` in the root of the repository.

## Writing automata

The simulator expects automata definitions to be written in a thin
Domain-Specific Language that wraps Python. Example implementations of
common distributed algorithms can be seen in
[`examples/specs`](examples/specs/). The language and simulation is more
thoroughly described in the tech report, which can be generated in the
`doc/` directory using `make report.pdf`.

When writing specifications, there are a few special pieces of state
available to you:

 - `self.i` is a unique per-node identifier
 - in outgoing transitions (i.e., those defined as tasks that have a
   `Transition-Output`), a variable named `to` holds the unique
   identifier of the neighbour currently being sent to.
 - in incoming transitions (i.e., those that appear in
   `Signature-Input`, and `connect` with an outgoing transition), a
   variable named `fr` holds the unique identifier of the neighbour that
   sent the current message.

In addition, an automata can, at any point, call the `mark` function to
change the color of the current node in the visualization, or the
`label` function to change the textual annotation for that node.

The simio parser, `src/parser/parser.py`, should be invoked on the
automaton specification to generate an executable automaton file:

    # Note that the output file *must* currently be called wtf.py
    ./src/parser/parser.py -f examples/specs/paxos.ioa > wtf.py

## Defining network graphs

A network graph should first be defined using the Graphviz [DOT
format](http://www.graphviz.org/content/dot-language). All edges
represent a FIFO channel, and all nodes in the graph will be running a
single instance of the automaton. Example graphs can be seen in
[`examples/graphs`](examples/graphs/).

## Visualizing behavior

To visualize how a given automaton behaves on a given graph, invoke the
simulator using:

    ./src/simulator/simulator.py -s .2 -g examples/graphs/complete.gv

This will open up a live view of the simulation in a new window, powered
by the simio [renderer](src/renderer/src/renderer/). If nothing opens,
you're probably missing `python2-pyinotify`. The `-s` option specifies
the time delay between each step of the simulation, and allows speeding
up or slowing down the visualization. `-t` can be used to keep every
intermediate visualization of the run.

The simulator's `STDOUT` will contain anything printed inside the
running automaton instances, while `STDERR` will contain messages from
the simulator.

## Included examples

To run one of the included examples, call `make`, and then run one of
the scripts in [`examples/demos`](examples/demos). Demos for
Bellman-Ford, Paxos, Peterson's leader-election algorithm, and Luby
Maximal Independent Set are given. You might want to run the examples
with `-s .2` so the simulation does not run too quickly to follow.
