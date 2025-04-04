program Ex35;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function comunsOrd(const a: TVetor; na: Integer; const b: TVetor; nb: Integer): Integer;
var
  i, j, count: Integer;
begin
  i := 0; j := 0; count := 0;
  while (i < na) and (j < nb) do
  begin
    if a[i] = b[j] then
    begin
      Inc(count);
      Inc(i);
      Inc(j);
    end
    else if a[i] < b[j] then
      Inc(i)
    else
      Inc(j);
  end;
  comunsOrd := count;
end;

var
  a, b: TVetor;
  na, nb, res, i: Integer;
begin
  na := 5; nb := 6;
  a[0] := 1; a[1] := 3; a[2] := 5; a[3] := 7; a[4] := 9;
  b[0] := 3; b[1] := 4; b[2] := 5; b[3] := 8; b[4] := 9; b[5] := 10;
  res := comunsOrd(a, na, b, nb);
  Write('Número de elementos em comum: ', res);
  Writeln;
end.
