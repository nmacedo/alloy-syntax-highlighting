// Fixture for the commands, no need to test these
sig A, B { var r : A }
pred p { }
pred q[a,b:univ] { }
assert c { }
fun f : univ { A }
fun g[a:univ] : univ { A }
fun h[] : univ -> univ { iden }

// Actual tests
run {}
run 
p for 3

run q 
for 2 /* comment */ but 3 A

run f  expect 1

run g for 3 A

run h for 3
  A , 3 int

run name p
run name // comment
f

run name { p }
run p p for
	3 but exactly 3 A, 4 int, 0 seq, 2..3 steps expect 0

check c for 1.. steps
check   name c
check c c for 3 but 3 A  
, 2 B, exactly 3 String, 4 Int
check name
{p
p}
expect 1
