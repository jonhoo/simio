package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"path"
	"regexp"
	"runtime"
	"strings"

	"container/list"

	graphviz "code.google.com/p/gographviz"
	shellwords "github.com/mattn/go-shellwords"
)

type HandleR int

const (
	QUIT HandleR = iota
	SUCCESS
	FAILURE
)

func findEdge(network *graphviz.Graph, n1 string, n2 string) (uint, *graphviz.Edge) {
	n1e := network.Edges.SrcToDsts[n1]
	if n1e != nil && n1e[n2] != nil {
		return 0, n1e[n2]
	}

	n2e := network.Edges.SrcToDsts[n2]
	if n2e != nil && n2e[n1] != nil {
		return 1, n2e[n1]
	}

	return 0, nil
}

func qprocess(edge *graphviz.Edge) {
	if qs[edge].Len() == 0 {
		delete(edge.Attrs, "label")
		delete(edge.Attrs, "color")
		delete(edge.Attrs, "arrowhead")
		return
	}

	edge.Attrs["labelfloat"] = "true"

	edge.Attrs["color"] = "blue"

	if qs[edge].Len() == 1 {
		edge.Attrs["label"] = q(fmt.Sprintf("%s", qs[edge].Front().Value))
		return
	}

	edge.Attrs["label"] = q(fmt.Sprintf("%s (+%d)", qs[edge].Front().Value, qs[edge].Len()-1))
}

var e2d map[*graphviz.Edge]string
var qs map[*graphviz.Edge]*list.List

func handle(cmd string, args []string, network *graphviz.Graph) (HandleR, string) {
	switch cmd {
	case "mark":
		{
			if len(args) != 2 {
				return FAILURE, fmt.Sprintf("Usage: mark <node> <color>")
			}
			node := network.Nodes.Lookup[args[0]]
			if node == nil {
				return FAILURE, fmt.Sprintf("[E] Unknown node: %s", args[0])
			}
			node.Attrs["color"] = q(args[1])
		}
	case "unmark":
		{
			if len(args) != 1 {
				return FAILURE, fmt.Sprintf("Usage: unmark <node>")
			}
			node := network.Nodes.Lookup[args[0]]
			if node == nil {
				return FAILURE, fmt.Sprintf("[E] Unknown node: %s", args[0])
			}
			delete(node.Attrs, "color")
		}
	case "send":
		{
			if len(args) != 3 {
				return FAILURE, fmt.Sprintf("Usage: send <from> <to> <msg>")
			}
			src, edge := findEdge(network, args[0], args[1])
			if edge == nil {
				return FAILURE, fmt.Sprintf("[E] No edge from node %s to node %s", args[0], args[1])
			}

			qs[edge].PushBack(args[2])
			qprocess(edge)

			_, ok := e2d[edge]
			if !ok {
				e2d[edge] = edge.Attrs["dir"]
			}

			if src == 0 {
				edge.Attrs["dir"] = "forward"
			} else {
				edge.Attrs["dir"] = "back"
			}
			edge.Attrs["arrowhead"] = "normal"
		}
	case "recv":
		{
			if len(args) != 2 {
				return FAILURE, fmt.Sprintf("Usage: recv <receiver> <sender>")
			}
			_, edge := findEdge(network, args[1], args[0])
			if edge == nil {
				return FAILURE, fmt.Sprintf("[E] No edge to node %s from node %s", args[0], args[1])
			}

			qs[edge].Remove(qs[edge].Front())
			qprocess(edge)

			if e2d[edge] == "" {
				delete(edge.Attrs, "dir")
			} else {
				edge.Attrs["dir"] = e2d[edge]
			}
		}
	case "erase":
		{
			e2d = make(map[*graphviz.Edge]string)
			qs = make(map[*graphviz.Edge]*list.List)
			for _, e := range network.Edges.Edges {
				qs[e] = list.New()
				qprocess(e)
				delete(e.Attrs, "dir")
			}
			for _, n := range network.Nodes.Nodes {
				delete(n.Attrs, "color")
			}
		}
	case "quit":
		return QUIT, ""
	default:
		return FAILURE, fmt.Sprintf("[E] Unknown command: %s", cmd)
	}
	return SUCCESS, "! " + cmd + " " + strings.Join(args, " ")
}
func q(i string) string {
	o := strings.Replace(i, "\\", "\\\\", -1)
	o = strings.Replace(o, "\"", "\\\"", -1)
	return "\"" + o + "\""
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "No network graph description given\n")
		os.Exit(2)
		return
	}

	data, err := ioutil.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "Could not read graph description: %s\n", err)
	}

	e2d = make(map[*graphviz.Edge]string)
	qs = make(map[*graphviz.Edge]*list.List)

	var spec []string
	var dot bytes.Buffer
	spec = nil
	indot := false
	for _, s := range strings.Split(string(data), "\n") {
		if indot {
			dot.WriteString("\n")
			dot.WriteString(s)

			indot = !strings.HasPrefix(s, "}")
			continue
		}

		m, _ := regexp.MatchString("(di)?graph\\s+{", s)
		if m {
			indot = true
			dot.WriteString(s)
		} else {
			spec = append(spec, s)
		}
	}

	tmpn, e := graphviz.Parse(dot.Bytes())
	if e != nil {
		panic(e)
	}
	network := graphviz.NewAnalysedGraph(tmpn).(*graphviz.Graph)

	for _, e := range network.Edges.Edges {
		qs[e] = list.New()
	}

	var start []*graphviz.Node
	start = nil
	for _, s := range spec {
		if strings.HasPrefix(s, "start ") {
			name := strings.TrimSpace(strings.TrimPrefix(s, "start"))
			start = append(start, network.Nodes.Lookup[name])
		}
	}

	for _, n := range start {
		if n == nil {
			continue
		}
		n.Attrs.Add("color", "red")
	}

	err = plot(network)
	if err != nil {
		panic(err)
	}

	in := bufio.NewReader(os.Stdin)
	for {
		cmd, err := in.ReadString('\n')

		if err != nil {
			if err == io.EOF {
				os.Exit(0)
			}
			panic(err)
		}

		iterate(network, strings.TrimSpace(cmd))
	}
}

func iterate(g *graphviz.Graph, command string) {
	args, _ := shellwords.Parse(command)

	var ok HandleR
	var out string
	switch len(args) {
	case 0:
		return
	case 1:
		ok, out = handle(args[0], args[0:0], g)
	default:
		ok, out = handle(args[0], args[1:], g)
	}

	fmt.Println(out)

	if ok == QUIT {
		os.Exit(0)
		return
	}

	if ok == FAILURE {
		return
	}

	err := plot(g)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Plotting exited with status code %s\n", err)
		os.Exit(1)
		return
	}

	// Redraw img
}

var started = false

func plot(g *graphviz.Graph) error {
	w, e := os.Create("next.svg")
	if e != nil {
		return e
	}

	var ebuf bytes.Buffer
	cmd := exec.Command("fdp", "-Tsvg")
	cmd.Stdin = bytes.NewReader([]byte(g.String()))
	cmd.Stdout = w
	cmd.Stderr = bufio.NewWriter(&ebuf)

	cmde := cmd.Run()
	w.Close()
	if cmde != nil {
		fmt.Fprintf(os.Stderr, "Failed to plot graph:\n---\n%s---\n%s", g.String(), ebuf.String())
		return cmde
	}

	e = os.Rename("next.svg", "current.svg")
	if e != nil {
		return e
	}

	if !started {
		started = true
		go func() {
			_, filename, _, _ := runtime.Caller(0)
			cmd := exec.Command(path.Join(path.Dir(filename), "show.py"), "current.svg")
			e := cmd.Run()
			if e != nil {
				fmt.Println(e)
			}
		}()
	}

	return nil
}
