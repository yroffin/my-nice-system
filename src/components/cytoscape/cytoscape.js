
export default {
  mounted: function () {
    if (!this.container) {
      console.log(this.nodes)
      let nodes = _.map(this.nodes, (node) => {
        return {
          "data": {
            "id": node.id
          }
        }
      })
      let edges = _.map(this.edges, (edge) => {
        return {
          "data": {
            "id": edge.id,
            "source": edge.source,
            "target": edge.target
          }
        }
      })
      let elements = []
      _.each(nodes, (node) => {
        elements.push(node)
      })
      _.each(edges, (edge) => {
        elements.push(edge)
      })
      this.container = cytoscape({
        container: document.getElementById("container"),
        elements: elements
      });
      // Appliquer un layout au graphe (par exemple, un layout circulaire)
      this.container.layout({
        name: 'circle'
      }).run();
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