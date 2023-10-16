
import { toto } from "sampleMylib"

export default {
  mounted: function () {
    if (!this.container) {
      this.container = cytoscape({
        container: document.getElementById("container"),
        elements: [ // liste des nœuds et des arêtes
          { // nœud A
            data: { id: 'a' }
          },
          { // nœud B
            data: { id: 'b' }
          },
          { // nœud C
            data: { id: 'c' }
          },
          { // arête AB
            data: { id: 'ab', source: 'a', target: 'b' }
          },
          { // arête BC
            data: { id: 'bc', source: 'b', target: 'c' }
          }
        ]
      });
      // Appliquer un layout au graphe (par exemple, un layout circulaire)
      this.container.layout({
        name: 'circle'
      }).run();

      this.value = 1
    }

  },
  template: `
  <div>
  <p>{{value}}</p>
  <div id="container" class="cy">
  </div>
  </div>
  `,
  data() {
    return {
      value: this.value
    }
  },
  methods: {
    handle_click() {
      this.value += 1;
      this.$emit("change", this.value);
    },
    reset() {
      this.value = toto;
    },
  },
  props: {
    title: String,
  },
};