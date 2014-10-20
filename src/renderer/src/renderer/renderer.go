package main

import (
	"bufio"
	"bytes"
	graphviz "code.google.com/p/gographviz"
	shellwords "github.com/mattn/go-shellwords"
	"fmt"
	"github.com/andlabs/ui"
	"image"
	"image/draw"
	"image/png"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"runtime"
	"regexp"
	"strings"
)

type areaHandler struct {
	img *image.RGBA
}

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

var e2d map[*graphviz.Edge]string
func handle(cmd string, args []string, network *graphviz.Graph) bool {
	switch cmd {
	case "mark":
		{
			node := network.Nodes.Lookup[args[0]]
			if node == nil {
				fmt.Fprintf(os.Stderr, "Unknown node: %s\n", args[0])
				return true
			}
			node.Attrs["color"] = q(args[1])
		}
	case "unmark":
		{
			node := network.Nodes.Lookup[args[0]]
			if node == nil {
				fmt.Fprintf(os.Stderr, "Unknown node: %s\n", args[0])
				return true
			}
			delete(node.Attrs, "color")
		}
	case "send":
		{
			src, edge := findEdge(network, args[0], args[1])
			if edge == nil {
				fmt.Fprintf(os.Stderr, "No edge from node %s to node %s\n", args[0], args[1])
				return true
			}

			edge.Attrs["label"] = q(args[2])
			edge.Attrs["color"] = "blue"
			edge.Attrs["labelfloat"] = "true"

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
			_, edge := findEdge(network, args[1], args[0])
			if edge == nil {
				fmt.Fprintf(os.Stderr, "No edge to node %s from node %s\n", args[0], args[1])
				return true
			}
			delete(edge.Attrs, "label")
			delete(edge.Attrs, "color")
			delete(edge.Attrs, "arrowhead")

			if e2d[edge] == "" {
				delete(edge.Attrs, "dir")
			} else {
				edge.Attrs["dir"] = e2d[edge]
			}
		}
	case "quit":
		return false
	default:
		{
			fmt.Fprintf(os.Stderr, "Unknown command: %s\n", cmd)
		}
	}
	return true
}
func q(i string) string {
	o := strings.Replace(i, "\\", "\\\\", -1)
	o = strings.Replace(o, "\"", "\\\"", -1)
	return "\"" + o + "\""
}

func (i *areaHandler) Paint(rect image.Rectangle) *image.RGBA {
	return i.img.SubImage(rect).(*image.RGBA)
}
func (i *areaHandler) Mouse(me ui.MouseEvent)  {}
func (i *areaHandler) Key(ke ui.KeyEvent) bool { return false }

var garea areaHandler
var graph ui.Area

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

	img, err := plot(network)
	if err != nil {
		panic(err)
	}

	done := false
	go ui.Do(func() {
		mx := img.Bounds().Max
		garea = areaHandler{img}
		graph = ui.NewArea(mx.X, mx.Y, &garea)
		stack := ui.NewVerticalStack(graph)
		stack.SetStretchy(0)
		done = true

		w := ui.NewWindow("Simio", mx.X, mx.Y, stack)
		w.OnClosing(func() bool {
			ui.Stop()
			return true
		})
		w.Show()
	})

	go func() {
		for !done {
			runtime.Gosched()
		}

		in := bufio.NewReader(os.Stdin)
		for {
			cmd, err := in.ReadString('\n')

			if err != nil {
				if err == io.EOF {
					ui.Stop()
					os.Exit(0)
				}
				panic(err)
			}

			// handle cmd
			args, _ := shellwords.Parse(strings.TrimSpace(cmd))
			if !handle(args[0], args[1:], network) {
				ui.Stop()
				os.Exit(0)
			}
			img, err = plot(network)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Plotting exited with status code %s\n", err)
				os.Exit(1)
				return
			}

			garea.img = img
			graph.RepaintAll()
		}
	}()

	err = ui.Go()
	if err != nil {
		panic(err)
	}
}

func plot(g *graphviz.Graph) (*image.RGBA, error) {
	var buf bytes.Buffer
	var ebuf bytes.Buffer
	cmd := exec.Command("fdp", "-Tpng")
	cmd.Stdin = bytes.NewReader([]byte(g.String()))
	cmd.Stdout = bufio.NewWriter(&buf)
	cmd.Stderr = bufio.NewWriter(&ebuf)

	cmde := cmd.Run()
	if cmde != nil {
		fmt.Fprintf(os.Stderr, "Failed to plot graph:\n---\n%s---\n%s", g.String(), ebuf.String())
		return nil, cmde
	}

	i, e := png.Decode(bufio.NewReader(&buf))
	if e != nil {
		return nil, e
	}

	b := i.Bounds()
	m := image.NewRGBA(image.Rect(0, 0, b.Dx(), b.Dy()))
	draw.Draw(m, m.Bounds(), i, b.Min, draw.Src)
	return m, nil
}
