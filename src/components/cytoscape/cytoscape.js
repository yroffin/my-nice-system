function build(cy, mygraph) {
  // refresh render
  cy.startBatch()
  //cy.boxSelectionEnabled(this.boxSelectionEnabled)
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

  cy.endBatch()
  cy.fit()

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
}

export default {
  mounted: function () {
    if (!this.container) {
      // builld container
      this.container = cytoscape({
        container: document.getElementById("container"),
        layout: { name: 'preset' },
        motionBlur: true,
        selectionType: 'single',
        boxSelectionEnabled: false
      });

      const emitNode = (evt) => {
        this.$emit("event", {
          type: evt.type,
          target: {
            id: evt.target.id(),
            data: evt.target.data(),
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

      // build graph
      build(this.container, this.model)
    }

  },
  methods: {
    handler() {
    }
  },
  template: `
  <div>
  <div id="container" class="cy">
  </div>
  </div>
  `,
  data() {
    return {
    }
  },
  methods: {
  },
  props: {
    title: String,
    model: Object,
    nodes: Array,
    edges: Array
  },
};