## dynetml2other

**dynetml2other** provides a set of tools for loading Dynamic Network Markup Language (DyNetML) files into the
<a href="http://igraph.org/python/">igraph</a> and <a href="http://networkx.github.io/">NetworkX</a> Python packages
for analyzing networks. It also supports a vanilla network format that uses dictionaries; while this format doesn't
support the graph libraries' ability to calculate network features, it should be much quicker for exploring
relationships between nodes.
 
### What is DyNetML?
 
<a href="http://www.casos.cs.cmu.edu/projects/dynetml/">DyNetML</a> is a GraphML-based format for specifying network
graphs, and is intended to support 'Meta-Networks' that combine multiple types of nodes that are related in many one-
and two-mode networks. It's the primary format used by the
<a href="http://www.casos.cs.cmu.edu/projects/ora/">ORA network analysis tool</a>.

### Why dynetml2other?

While potent, ORA is designed to be used through a GUI and doesn't allow users to manipulate or work with their data
in a programmatic fashion; this makes systematic use of the tool largely impossible. dynetml2other provides a workaround
for this by allowing users to load DyNetML files into graph libraries for Python. Users can manipulate these graphs,
calculate necessary metrics, and then save out the changed results as DyNetML files or any other format of choice.

### What dynetml2other Is Not:

dynetml2other is _not_ a full-featured replacement for ORA or many of its reports.

### What dynetml2other Is:

dynetml2other is a way to use igraph or NetworkX to analyze networks stored in DyNetML. It provides tools for
manipulating DyNetML data that approximate a small number of ORA's tools form manipulation, and allows users to save
out their work for further manipulation in ORA or other tools.