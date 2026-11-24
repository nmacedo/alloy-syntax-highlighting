module examples/graphs[Node, 
   Edge]

open util/ordering[Node] as ord
open util/graph[Node]
open util/integer as integer


open util/ /* path comment */ ordering[Node] as commented
open util/ /*attached comment*/ relation as rel

open util/ordering[
  Node
] as multiline

open util/ordering // trailing path comment
[Node] as lineCommented

open util/ordering[/* path argument comment */ Node] as commentedArgument
open util/integer let macroAfterOpen = univ

