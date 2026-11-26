// Fixture for the declarations, no need to test these
sig X { a: univ }
sig A, B, C in X {}
run {}

// Facts
fact {
	some A
}

fact name {
	some A
}

fact "name string" {
	some A
}

fact emptyFact { }

fact "named empty fact" 
{ }

fact f{ { all a:A | a in univ }}

// Predicates
pred p1 {
	some A
}

pred p2 {}

private pred q[

] {	some A 
}

pred q1[x,y :A] {
	some A
}

pred q2[x,y :A, z: A , w = B] { some a:A | a in univ }

pred q[disj x,y :A, z : one A , disj w: set B] {
	some A
}

pred r[x : A -> B] {}

pred ch[x : {a : A | a in univ}] { x -> x in univ some -> lone univ }

pred ch2[x : {a : { x : univ | x in univ } | a in univ}] { no none }

pred emptyPred { }
pred emptyPred2[] { }
pred emptyPred3[
] { }

pred pp[a : some A implies B else C] { }
pred qq[a : A = B implies B else C, b=univ] { }

// Functions
fun p : univ {
	A
}

private fun q[
] :
univ -> one univ { B -> B }

fun q[x,y :A, z: A , w,u = B] : univ lone -> A {
	x -> y
}

fun q[disj x,y :A, z: one A , disj w: set B] : A -> one (B lone -> C) {
	A -> B -> C
}

fun r[x : A -> B] : one A {
	A
}

fun emptyFun : univ { A }
fun emptyFun2[] : univ { A }
fun emptyFun2_multiline[
] : univ { A }

fun f[x : {a:univ | some a }, y : univ-A] : univ { univ }

fun s : {x:univ | x in A} { A }
fun t[a: {x:univ | x in A}] : A { A }
fun u : {{A}+{A}} { A }
fun v : A -> {A} -> {{A}} { A->A->A }

fun ff[a : A = B implies B else C] : B in C implies B else B + A { univ }

fun rt_identifier : A { A }
fun rt_number : 42 { Int }
fun rt_group : (A + B) { A }

fun rt_string : "text" { String }

fun rt_block_end : {A} { A }
fun rt_nested_blocks : {{A} + {{B}}} { A }
fun rt_block_middle : A -> {B} -> {{C}} { A -> iden }
fun rt_multiline_type : A ->
  {B} ->
  C {{ A -> iden }}
fun rt_body_next_line : A
{ A }
fun rt_block_comment_boundary : A /* comment */ { A }
fun rt_line_comment_boundary : A // comment
{ A }
fun rt_multiline_comment_boundary : A /* comment
*/ { A }
fun rt_nested_block_body_next_line : {{A}+{B}}
{ A }

fun rt_sibling_blocks_in_comprehension :
  {x: univ | {some x} and x in A} -> B
  { A -> univ }

fun rt_nested_comprehension_blocks :
  {x: univ | {some x} and {{some x} or {no x}}} -> C
  { iden }

fun rt_relation_with_interleaved_blocks :
  A -> {B} -> {{C} + {A}} -> B
  { {A} -> {B} -> {A -> C} }

fun rt_grouped_blocks_in_return_type :
  ({A} + {{B} - {C}}) -> {A} -> B
  { A->univ->B }

fun rt_comprehension_in_middle_of_relation :
  A -> {x: univ | {{x in B}  {some x}}} -> {C}
  { {A -> A} -> B }

fun rt_nested_comprehension_in_return_type :
  {x: univ | x in A and some {y: univ | y in B and y = x}} -> C
  { {A} -> B }

fun rt_nested_comprehensions_as_relation_operands :
  {x: univ | x in A} -> {{y: univ | y in B} + {C}} -> B
  { A -> A -> A }

fun rt_multiline_blocks_and_body :
  A ->
  {B} ->
  {{C} + {B}}
  { A -> {A -> A} }

fun rt_comments_after_nested_return_block :
  A -> {{B} + {C}} /* body follows */ { A -> univ }

fun rt_body_after_comprehension_siblings :
  {x: univ | {{some x} {some x}} } { A }

fun rt_body_after_comprehension_siblings2 :
  {x: one univ {one x one x} } { one A implies A else univ }


// Assertions 
assert p { some A }

assert "p name" { }

assert {
  no none
 }

// Macros
let mcr = univ
let mcr2[x] = x + x
let mcr3[x] = { x +
 x }
let mcr4[x,y,z] = { x implies z else z }

let mcr5 = let x = 10, y = univ | x in y

let mcr6 = let x = 10 | let y = univ | x in y

let mcr7 = let x = 10 {
	 let y = univ | x in y }

pred x { mcr5 mcr6 }

// Let-expressions
fact letVariations {
  let x = A |
    x in univ

  let x = A, y = B |
    x in y

  some (let x = A | x + let y = x | y)

  let x = A + B |
    let y = C |
      x -> y in iden

  let a = {x : A | x in B} , b = {y : C | some y} |
      a -> b in iden

  (let x = 5 | x + 1) = 6

  (let x = A | some x) and (let y = B | no y)

  let x = univ {
		x in {let y = univ { y }}
	}
}

// Top-level macro brace bodies, with and without parameters
let macroBlock { A = B }
let macroBlockParams[x,y] { x = y }
let macroComparison[x] = x = A

pred afterMacros { macroBlock || macroBlockParams[A,B] || macroComparison[A] }

fact letBindingComments {
  let a = {x : A | some x},
      /* comment */ b
        = {y : B | some y} |
    a = b
}

fact letRhsComparison {
  let c = A = B |
     c
}

fact letRhsLogicalOr {
  let c = some A || some B |
    c 
}

let inlineMacroBoundary = univ /* next declaration */ private pred afterInlineMacroBoundary { some A }
let inlineBlockMacro { some A } fun afterInlineBlockMacro: A { A }

let macroBlockNestedLet {
  let x = A |
    let y = x |
      some y
}

let inlineMacroBeforeLet = univ let followingInlineMacro = univ

// Initial let chains are expression prefixes, even across comments and lines.
let initialLetComments = /* first */ // still awaiting the expression
  -- still awaiting the expression
  /* second */ let x = univ |
    let y = x | y

let initialLetAdjacent = let x = univ | x let afterInitialLetAdjacent = univ
let initialLetComparison = let x = univ | x = univ
let initialLetLineComparison = let x = univ | x
  = univ
pred afterInitialLetChains { some univ }

// Still requires tracking an operand position inside an undelimited macro RHS.
let remainingLetAfterOperator = univ + let x = univ | x

// Comments and line breaks between callable header tokens.
pred /* keyword/name gap */ headerBlockBeforeName[x = A] {}
fun headerBlockBeforeBracket /* name/bracket gap */ [x = A]: A { x }
pred /* keyword/name
  gap */ headerMultilineBlock /* name/bracket
  gap */ [x = A] { some x }
fun // keyword/name gap
  headerLineComments // name/bracket gap
  [x = A]: A { x }
pred
  headerSplit
  [x = A] { some x }

// Nested expressions retain comparisons and own their brackets and commas.
pred /** keyword/name gap */ headerNested -- name/bracket gap
  /* before parameters */ [
    x = (A = B implies A else B),
    y: iden[A],
    z = {a: A | a = a}
  ] { x = x }

// Optional parameters: stop the header before the return type or body.
pred /* gap */ headerNoParamsPred // body follows
  { let x = A | x = A }
fun /* gap */ headerNoParamsFun -- return type follows
  : A = B implies A else B { A }
fact afterSplitHeaders { A = A }

// Comment delimiters shield header punctuation; spaces are not required.
pred/* : { [ ] } */headerTight[x = A] { some x }
fun headerTightFun/* : { [ ] } */[x = A]: A { x }

// Parameter multiplicities after the declaration separator.
pred boundaryParameterControl[x: one univ] { some x }
pred boundaryParameterComment[x: /* gap */ one univ] { some x }
pred boundaryParameterSplit[x:
  lone univ] { some x }
pred boundaryParameterLineComment[x: // gap
  some univ] { some x }
