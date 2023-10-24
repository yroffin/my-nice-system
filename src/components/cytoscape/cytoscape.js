function build(cy, mygraph) {
  // refresh render
  cy.startBatch()
  cy.nodes().remove()
  cy.edges().remove()

  if (mygraph.nodes) {
    const mynodes = _.map(mygraph.nodes, (node) => {
      return {
        data: {
          id: node.id,
          label: node.label,
          cdata: node.cdata,
          alias: node.alias,
          group: node.group,
          tag: node.tag
        },
        position: {
          x: node.x,
          y: node.y
        }
      }
    })
    cy.add(mynodes)
  }

  if (mygraph.edges) {
    const myedges = _.map(mygraph.edges, (edge) => {
      return {
        data: {
          id: edge.id,
          label: edge.label,
          source: edge.source,
          target: edge.target,
          _source: edge._source,
          _target: edge._target,
          tag: edge.tag
        }
      }
    })
    cy.add(myedges)
  }

  const content = (element) => {
    let cdata = element.data().cdata ? '*' : ''
    let alias = element.data().alias ? '@' : ''
    if (element.data().label && element.data().group) {
      return `${element.data().label} (${element.data().group}) ${cdata} ${alias}`
    }
    if (element.data().label) {
      return `${element.data().label} ${cdata} ${alias}`
    }
    return ""
  }

  const mystyle = _.map(mygraph.styles, (tag) => {
    if (!tag.label) {
      let result = {
        selector: `${tag.selector}`,
        style: tag.style,
      }
      result.style.content = content
      return result
    } else {
      let result = {
        label: tag.label,
        selector: `${tag.selector}[tag = '${tag.label}']`,
        style: tag.style
      }
      result.style.content = content
      return result
    }
  })

  cy.style(mystyle)
  cy.endBatch()
  cy.fit()
}

export default {
  mounted: function () {
    if (!this.container) {
      // builld container
      this.container = window.container = cytoscape({
        container: document.getElementById("container"),
        layout: { name: 'preset' },
        motionBlur: true,
        selectionType: 'single',
        boxSelectionEnabled: false
      });

      // Add cytoscape edgehandles
      let defaults = {
        canConnect: function (sourceNode, targetNode) {
          // whether an edge can be created between source and target
          return !sourceNode.same(targetNode); // e.g. disallow loops
        },
        edgeParams: function (sourceNode, targetNode) {
          // for edges between the specified source and target
          // return element object to be passed to cy.add() for edge
          return {};
        },
        hoverDelay: 150, // time spent hovering over a target node before it is considered selected
        snap: true, // when enabled, the edge can be drawn by just moving close to a target node (can be confusing on compound graphs)
        snapThreshold: 50, // the target node must be less than or equal to this many pixels away from the cursor/finger
        snapFrequency: 15, // the number of times per second (Hz) that snap checks done (lower is less expensive)
        noEdgeEventsInDraw: true, // set events:no to edges during draws, prevents mouseouts on compounds
        disableBrowserGestures: true // during an edge drawing gesture, disable browser gestures such as two-finger trackpad swipe and pinch-to-zoom      
      }
      this.edgehandles = this.container.edgehandles(defaults)
      this.snapToGrid = this.container.snapToGrid({
        gridSpacing: 100
      })

      const emitNode = (evt) => {
        this.$emit("event", {
          type: evt.type,
          target: {
            id: evt.target.id(),
            data: evt.target.data(),
            position: {
              x: evt.target.position().x,
              y: evt.target.position().y
            },
            type: 'node'
          }
        });
      }

      const emitEdge = (evt) => {
        console.log(evt)
        this.$emit("event", {
          type: evt.type,
          target: {
            id: evt.target.id(),
            data: evt.target.data(),
            type: 'edge'
          }
        });
      }

      const emitEdgeHandle = (evt, sourceNode, targetNode, addedEdge) => {
        console.log(addedEdge)
        this.$emit("edgehandle", {
          type: evt.type,
          sourceNode: sourceNode.data(),
          targetNode: targetNode.data(),
          addedEdge: addedEdge.data()
        });
      }

      this.container.on('zoom', (event) => {
      });

      this.container.on('dblclick', 'node', (event) => {
        emitNode(event)
      });

      this.container.on('dblclick', 'edge', (event) => {
        emitEdge(event)
      });

      this.container.on('cxttap', 'node', (event) => {
        emitNode(event)
      });

      this.container.on('cxttap', 'edge', (event) => {
        emitEdge(event)
      });

      this.container.on('click', (event) => {
      });

      this.container.on('click', 'node', (event) => {
        emitNode(event)
      });

      this.container.on('click', 'edge', (event) => {
        emitEdge(event)
      });

      this.container.on('mouseover', 'node', (event) => {
        emitNode(event)
      });

      this.container.on('mouseover', 'edge', (event) => {
        emitEdge(event)
      });

      this.container.on('mouseout', 'node', (event) => {
        emitNode(event)
      });

      this.container.on('mouseout', 'edge', (event) => {
        emitEdge(event)
      });

      this.container.on('ehcomplete', (event, sourceNode, targetNode, addedEdge) => {
        emitEdgeHandle(event, sourceNode, targetNode, addedEdge)
      });

      // build graph
      build(this.container, this.model)
    }

  },
  methods: {
    select(data) {
      this.container.center(this.container.$(`#${data}`))
    },
    dropNode(data) {
      this.container.$(`#${data.id}`).remove()
    },
    dropEdge(data) {
      console.log(data)
      this.container.$(`#${data.id}`).remove()
    },
    cloneNode(data) {
      let cloned = {
        data: {
          id: data.id,
          label: data.data?.label,
          alias: data.data?.alias,
          cdata: data.data?.cdata,
          group: data.data?.group,
          tag: data.data?.tag
        },
        position: {
          x: data.position?.x,
          y: data.position?.y
        }
      }
      this.container.add(cloned)
    },
    getNodes() {
      this.$emit("nodes", _.map(this.container.nodes("#"), (node) => {
        return {
          data: node.data(),
          position: node.position()
        }
      }));
    },
    /**
     * start draw mode
     * @param {*} data 
     */
    start(data) {
      let selected = this.container.$(`#${data.id}`)
      this.container.center(selected)
      this.edgehandles.start(selected)
    },
    /**
     * fi draw mode behaviour
     * @param {*} enable 
     */
    drawMode(enable) {
      if (enable) {
        this.edgehandles.enableDrawMode()
      } else {
        this.edgehandles.disableDrawMode()
      }
    }
  },
  template: `
  <div class="cy">
    <div id="container" class="cy">
    </div>
  </div>
  `,
  data() {
    return {
    }
  },
  props: {
    title: String,
    model: Object,
    nodes: Array,
    edges: Array
  },
};