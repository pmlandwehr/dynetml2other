## dynetml2other

**dynetml2other** provides a set of tools for loading Dynamic Network Markup Language (DyNetML) files into the
 <a href="http://igraph.org/python/">igraph</a> and <a href="http://networkx.github.io/">NetworkX</a> Python packages
 for analyzing networks; a vanilla network format using dictionaries is also available if richer network analysis
 capabilities are unnecessary. <a href="http://www.casos.cs.cmu.edu/projects/dynetml/">DyNetML</a> is a GraphML-based format
 for specifying network graphs, and is intended to support 'Meta-Networks' that combine multiple types of nodes that are
 related in many one- and two-mode networks. It's the primary format used by the
 <a href="http://www.casos.cs.cmu.edu/projects/ora/">ORA network analysis tool</a>. While potent, ORA is designed to be
 used through a GUI and doesn't allow users to manipulate their data in a programmatic fashion. dynetml2other is
 intended to provide a workaround for this by allowing users to load DyNetML files into graph libraries for Python.
 Users can manipulate their graphs and calculate particular network metrics, then save them back out into DyNetML or
 other formats of choice.

### What dynetml2other Is Not

dynetml2other is _not_ a full-featured replacement for ORA or many of its reports.

### What dynetml2other Is

dynetml2other is a way to use igraph or NetworkX methods to analyze meta-networks. It provides some tools
(and hopefully additional ones in the future) for manipulating DyNetML data that approximate a small number of ORA's
features. It also provides tools for saving out your networks in a DyNetML format.