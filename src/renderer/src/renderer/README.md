Simio simulation renderer. Reads the Graphviz DOT graph file passed in as the
first argument, renders it as an SVG, and passes it to `show.py`. It then
accepts visualization commands on STDIN, rerenders the graph, and `show.py`
automatically displays the updated graph render.
