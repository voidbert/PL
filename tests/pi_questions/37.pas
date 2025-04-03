program Ex37;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function minInd(const v: TVetor; n: Integer): Integer;
var
  i, minIndex: Integer;
begin
  if n = 0 then
  begin
    minInd := -1;
    Exit;
  end;
  minIndex := 0;
  for i := 1 to n - 1 do
    if v[i] < v[minIndex] then
      minIndex := i;
  minInd := minIndex;
end;

var
  v: TVetor;
  n, index, i: Integer;
begin
  n := 6;
  v[0] := 7; v[1] := 3; v[2] := 9; v[3] := 1; v[4] := 4; v[5] := 2;
  index := minInd(v, n);
  Write('O menor elemento é ', v[index], ' no índice ', index);
  Writeln;
end.
