// Fixture, no need to test these
sig A, B, C {
    r, s: set A,
    var t, u : set B
}
var sig X in B {
    var a, b : set C
}
run {}

fact {
    static$ in field$
    all s : sig$ | some s.fields

    some A$.parent

    all f : A$.subfields | some f.value

    no X$b.value

    all v: var$ | v.value != v.value'
}

