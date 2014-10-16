package main

import (
	"bufio"
	graphviz "code.google.com/p/gographviz"
	"fmt"
	"github.com/andlabs/ui"
	"image"
	"image/png"
	"image/draw"
	"io"
	"io/ioutil"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"bytes"
)

type areaHandler struct {
	img *image.RGBA
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

	var spec []string
	var dot bytes.Buffer
	spec = nil
	indot := false
	for _,s := range strings.Split(string(data), "\n") {
		if indot {
			dot.WriteString("\n")
			dot.WriteString(s)

			indot = !strings.HasPrefix(s, "}")
			continue
		}

		m, _ := regexp.MatchString("graph\\s+{", s)
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
	for _,s := range spec {
		if strings.HasPrefix(s, "start ") {
			name := strings.TrimSpace(strings.TrimPrefix(s, "start"))
			start = append(start, network.Nodes.Lookup[name])
		}
	}

	for _,n := range start {
		if n == nil {
			continue
		}
		n.Attrs.Add("color", "red")
	}

	img, err := plot(network)
	if err != nil {
		panic(err)
	}

	go ui.Do(func() {
		mx := img.Bounds().Max
		garea = areaHandler{img}
		graph = ui.NewArea(mx.X, mx.Y, &garea)
		stack := ui.NewVerticalStack(graph)
		stack.SetStretchy(0)

		w := ui.NewWindow("Simio", mx.X, mx.Y, stack)
		w.OnClosing(func() bool {
			ui.Stop()
			return true
		})
		w.Show()
	})

	go func() {
		in := bufio.NewReader(os.Stdin)
		for {
			cmd, err := in.ReadString('\n')

			if err != nil {
				if err == io.EOF {
					break
				}
				panic(err)
			}

			// handle cmd
			args := strings.Split(strings.TrimSpace(cmd), " ")
			switch (args[0]) {
				case "mark": {
					node := network.Nodes.Lookup[args[1]]
					if node == nil {
						fmt.Fprintf(os.Stderr, "Unknown node: %s\n", args[1])
						break
					}
					node.Attrs.Add("color", "green")
				}
			}
			img, err = plot(network)
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
	cmd := exec.Command("dot", "-Tpng")
	cmd.Stdin = bytes.NewReader([]byte(g.String()))
	cmd.Stdout = bufio.NewWriter(&buf)
	cmd.Run()
	i, e := png.Decode(bufio.NewReader(&buf))
	if e != nil {
		return nil, e
	}

	b := i.Bounds()
	m := image.NewRGBA(image.Rect(0, 0, b.Dx(), b.Dy()))
	draw.Draw(m, m.Bounds(), i, b.Min, draw.Src)
	return m, nil
}
