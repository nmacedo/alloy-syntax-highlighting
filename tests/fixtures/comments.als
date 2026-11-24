// Line comment before declaration
pred commentTest1 {
  // Comment inside body
  some A
  -- Another comment
  and some B
}

pred commentTest2 {
  /* Block comment in formula */
  some A
  /* Multi-line
     block
     comment */ and some B
}

// Comment between quantifier and variable
pred commentTest3 {
  all // comment here
    /* comment */ x : A | some x
}

pred commentTest4 {
  all x : -- comment in type
    A | some x
}

// Comments in comprehensions
pred commentTest5 {
  {x : // comment in var type
    A | // comment after pipe
    x in B // comment after formula
  } in univ
}

// Comments in parameter lists
pred commentTest6[
  // comment in params
  x : /* comment */ A,
  // another comment
  y : B
] {
  x -> y /* comment 
     comment */ in univ
}

-- Double-dash line comment
/** Documentation comment. */
pred documentedComment { some A }
