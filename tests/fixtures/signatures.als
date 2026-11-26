sig A { a : univ }

sig
B in A {} { some none }

var abstract sig M  {
}

private sig C,
D in B
{}

one sig E in A+none + this/C {}

sig F = E+C+seq/Int   {
b : Int
}

var lone sig G in A { var c, d, e: A, var g,h,f : B, }

one var sig H in G+D+univ {}

abstract private some var sig I,J, K
    extends M {} {
    some none
    no none
}

sig X {
    a, b : this/A,
    c : set B,    var d : one C,
    disj e, f : A -> univ,
    h, i, j: disj A -> B,
    k : A lone -> one Int,
    private l : A set -> String,
    m : seq A set -> some A,
    n : A->B ->   C,
    o : (A lone ->B) one ->C,
    p : A some -> one (B set ->C),
    var q : A -> B -> C -> D,
    var private disj x,y : disj A one -> lone (B set -> some D),
    z : { x : univ | some x},
}

sig Y {
    ay : univ,
    by : ay,
    cy : ay -> one by,
    dy : set ay - by,
    ey : @ay,
    fy : @ay.by,
    gy : this.@ay
} {
    ay in by
    this.cy in by
    @ay in cy
}

sig FieldDefaults {
  a = univ,
  b = A + B + C,
  c = A = B implies C else B,
  d : A = B implies C else B,
}

// Enumerations
enum Color { RED, GREEN, BLUE }
enum Size { S, MM, 
LL
, XL 
}
enum Single { ONLY }

// Fixture, no need to test these
run {} for 0 but 1 int, 2 steps

// Long whitespace checks that signature-hierarchy context survives history compaction.
sig                                                                                Child in A {}


// Signature modifiers need to survive comments and line breaks before sig.
one /* same-line gap */ sig BoundarySigControl {}
one
sig BoundarySigSplit {}
lone // keyword follows on the next line
sig BoundarySigLineComment {}
some /* split
  gap */ sig BoundarySigBlockComment {}

// Field multiplicities after the declaration separator.
sig BoundaryFields {
  control: one univ,
  commented: /* gap */ one univ,
  split:
    lone univ,
  lineComment: // gap
    some univ
}
