// Fixture for the declarations, no need to test these
sig X { a : X }
sig A,B,C,D in X {}

pred multiplicityRoles {
  // Quantifiers and multiplicity checks
  all x: A |  some y: B | x -> y in a
  no disj x, y: A | x = y
  one x: A |    lone x
  lone x: A | one x
  some x: A | some   x
  no x: A | no x

  // Multiplicity modifiers in variable declarations
  all x: one  A |  some x
  all y: lone A | one y
  all z:  some A | lone z
  all w: set A | no w

  // Multiplicity checks, not declaration modifiers
  some A
  lone B
  one C
  no A

  // Arrow checks
  a in A lone -> some B
  a -> univ in A lone -> some B set -> one C
}

pred comprehensions {
  some { x: A | x in B and some x }
  { x: A | some x and x in B } in A
  some iden + { x: A | all y: B | x -> y in a } -> { y: B | no y }
  no { x: A, y: B | x = y }
  some { x: A | some { y: B | x -> y in a } and x in A }
  lone { x: A | { y: B | some y } in B }
}

pred propositionalOperators {
	(some A) or (some A) || (some A)
	iff		(some A)

	(some A) => (some A) or (some A) && not (some A)
}

pred relationalOperators {
  A + B - C & D in univ
  A -> B ++ C -> D in iden
  A <: B in univ
  A :> B in univ
  A . a in univ
  ^a in iden
  *a in iden
  ~a in a

  ^(iden + a) in iden
  *(A -> B) in univ->univ
  ~(A -> B) in univ->univ

  ~~iden in a
  ^^^a in iden
  ^~a in a

  // Domain/range restriction
  A <: (B -> C) in a
  (A -> B) :> C in a
  A <: B :> C in univ

  // Join with complex operands
  A . (a . a) in univ
  (a + univ -> univ) . (a + iden) in univ->A
  a.a.a.a.a in a

  A not = B or C != D
  A in B and C not in D
  
  A = B
  A in B
  A !in B or B not in A or not B in A or ! A ! in B

  some A and no B or no C implies some D iff lone A
}

pred ternaryConditionals {
  some A implies some B else lone C

  ((A = B) implies A else B) = univ
  no ((some A and no B) implies C else D)

  some A => no (some B implies C else D) else some D
  some (some A implies B else (some C => D else D))
  (some A implies (some B implies C else D) else (some D implies A else B)) = univ

  (some A => B else C) in univ and some D
  no (some A implies univ else none)
}

fact {
	{} {} {}
	{} and {}
	{
		{(some A)
(some A)} {}
	}
}

pred temporalOperators {
  always eventually some A
  after (some A) until before some B
  historically no A since once lone B
  some A releases no B
  some A triggered no B
}

fact {
  some x: some A | some x and x -> x -> x in A some -> some A -> some A

  one disj a,b:one univ, x,y:one univ {
    one a->b
    a->x in a one -> one y
  }

  no x: set A | x -> x in A set -> set A and no x+x
}

pred arrowComplexity {
  iden -> iden in A one -> B lone -> C some -> D
  iden -> iden in  A  set -> B set -> C set -> D
  iden -> iden in A -> B -> C -> D 

  iden in (A + B) -> (C + D)
  iden in (A - B) lone -> (C & D) 

  {x : one A, y : one B | x->y in a} in iden
  {x : A, y : B, z : C | x -> y -> z in iden -> univ} in iden -> univ
}

pred comprehensionVariations {
 
  // Single variable, no guard
  {x : A} in univ

  // Single variable with guard
  {x : A | some x} in univ

  // Multiple variables, single guard
  {x : A, y : B | x = y} in iden

  // Multiple guards
  {x : A | x in B and x in C and some x} in univ

  // Nested comprehensions
  {x : A | some {y : B | x -> y in a}} in A
  {x : A | some {y : B | lone {z : C | x -> y -> z in a->univ}}} in univ

  // Comprehension as operand in complex expressions
  {x : A | x in B} + {y : B | some y} in univ
  {x : A | x = A} - {y : B | y in A} in univ

  // Comprehension with implicit conjunction (newlines in expression)
  {x : A |
    { x in B
    some x }
  } in univ

  // Comprehension with disj
  no {disj x, y : A | x != y}

  // Comprehension with multiplicity modifiers
  {x : one A | some x} in univ
  lone {x : one A, y : one B | x -> y in a}
 
  // Block comprehension
  some {x : A { x in univ } }
  some {x : A { x in {y : univ { y in univ }} } }}

pred multiplicitiesWithComments {
  all x: /* comment before multiplicity */ one A | some x
  iden in A one /* comment before arrow */ -> B
  iden in A -> /* comment before multiplicity */ one B
}

pred multiplicitiesAcrossLineComments {
  all x: /* first */ // comment after the separator
    /* second */ one A | some x
  iden in A one /* first */ // comment before the arrow
    /* second */ -> B
  iden in A -> /* first */ // comment after the arrow
    /* second */ one B
  some A
}


// The same line prefix as an arrow modifier can instead end with a test.
pred multiplicityWithoutFutureArrow {
  none in none one /* first */ // the next line contains no arrow
    /* second */ univ
}

// A comprehension RHS must not end the enclosing let binding list.
pred boundaryLetComprehensions {
  let x = {a: univ | a = a}, y = univ | y = y
  let x = {
    a: univ | a = a
  }, splitY = univ | splitY = splitY
  let x = { /* gap */ a: univ | a = a}, commentY = univ | commentY = commentY
}
