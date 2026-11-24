// Numerical literals
fact {
  // Decimal numbers with underscores (separators for readability)
  1000 + 2000000 + 999 = 3001000

  // Hex numbers with various cases and underscores
  0xFF + 0xff + 0xAB_CD_EF = 0x11
  0x03 + 0x00 + 0xDE_BE = 0xDA

  // Binary numbers
  0b101 + 0b1_0_1 + 0b1111_0000 = 0b0
  0b1 + 0b11111111 = 0b0

  // Combinations and edge cases
  0 + 00 + 000 = 1
}

// String literals
fact {
  // Basic strings
  "hello" = "world"

  // Strings with escape sequences
  "line1\nline2" in univ
  "tab\\there" in univ
  "quote\"inside" in univ
  "backslash\\ again" in univ
  "carriage\\rreturn" in univ
  "form\"ffeed" in univ
  "backspace\nbtest" in univ

  // String with multiple escapes
  "path\\to\\file\nNext line with \"quotes\"" in univ

  // String with only spaces
  "   " in univ
}

sig A,B in Int {}

fact {

  A < B
  A > B
  A =< B
  A >= B
  A < B or A > B
  A =< B and B >= A


  #A in univ
  #(A + B) = 5
  add[1, 2] = 3
  sum A = 0
  int[1] = -2

  0 = (sum x:A | #x)

  add[1, 2] = 3
  mul[2, 3] = 6
  div[10, 2] = 5
  5 >> 3 = 3 << 3

  // Structural functions
  sum A = 5
  int[0xFF] = 255
	
}

run { String + Int in univ } for 2 but 3 int, exactly 4 String
