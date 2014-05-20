## dynetml2other

**dynetml2other** provides a set of tools for loading Dynamic Network Markup Language (DyNetML) files into the <a href="http://igraph.org/python/">igraph</a> and <a href="http://networkx.github.io/">NetworkX</a> Python packages for analyzing networks. <a href="http://www.casos.cs.cmu.edu/projects/dynetml/">DyNetML</a> is a freely-usable XML-based format for specifying network graphs. It is the primary format used by the <a href="http://www.casos.cs.cmu.edu/projects/ora/">ORA network analysis tool</a>. While a potent tool for network analyses, ORA is designed to be used through a GUI and doesn't allow users to manipulate their data in a programmatic fashion. dynetml2other is intended to provide a workaround for this by allowing users to load DyNetML into graph libraries for Python. Users can manipulate their graphs and then save them back out into other formats

### What dynetml2other Is Not

dynetml2other is _not_ a full-featured replacement for ORA or many of its reports.

### What dynetml2other Is

dynetml2other is a way to use igraph or networkx methods to analyze networks. It provides some tools (and hopefully additional ones in the future) for manipulating DyNetML data. It also provides tools for saving out your networks in a DyNetML format, so that you can move them back into ORA. If DyNetML isn't part of your workflow, you might be better served by just using networkx or igraph directly.
