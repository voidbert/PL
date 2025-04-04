program Ex39;
const
  MAX = 10;
type
  TMatrix = array[0..MAX-1, 0..MAX-1] of Real;

function triSup(N: Integer; m: TMatrix): Integer;
var
  i, j: Integer;
begin
  for i := 1 to N - 1 do
    for j := 0 to i - 1 do
      if m[i][j] <> 0 then
      begin
        triSup := 0;
        Exit;
      end;
  triSup := 1;
end;

var
  m: TMatrix;
  N, i, j: Integer;
begin
  N := 3;
  m[0][0] := 1; m[0][1] := 2; m[0][2] := 3;
  m[1][0] := 0; m[1][1] := 4; m[1][2] := 5;
  m[2][0] := 0; m[2][1] := 0; m[2][2] := 6;

  if triSup(N, m) = 1 then
    Writeln('A matriz é triangular superior.')
  else
    Writeln('A matriz NÃO é triangular superior.');
end.
