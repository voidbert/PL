program Ex36;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function contem(v: TVetor; n, x: Integer): Boolean;
var
  i: Integer;
begin
  contem := False;
  for i := 0 to n - 1 do
    if v[i] = x then
    begin
      contem := True;
      Exit;
    end;
end;

function comuns(a: TVetor; na: Integer; b: TVetor; nb: Integer): Integer;
var
  i, j, count: Integer;
  jaContado: array[0..MAX-1] of Boolean;
begin
  for i := 0 to na - 1 do
    jaContado[i] := False;

  count := 0;
  for i := 0 to na - 1 do
  begin
    if not jaContado[i] then
    begin
      if contem(b, nb, a[i]) then
        Inc(count);
      for j := i + 1 to na - 1 do
        if a[j] = a[i] then
          jaContado[j] := True;
    end;
  end;
  comuns := count;
end;

var
  a, b: TVetor;
  na, nb, res, i: Integer;
begin
  na := 7; nb := 6;
  a[0] := 5; a[1] := 3; a[2] := 5; a[3] := 7; a[4] := 2; a[5] := 3; a[6] := 9;
  b[0] := 1; b[1] := 3; b[2] := 5; b[3] := 9; b[4] := 10; b[5] := 5;
  res := comuns(a, na, b, nb);
  Write('Número de elementos distintos em comum: ', res);
  Writeln;
end.
