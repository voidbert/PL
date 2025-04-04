program Ex34;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function elimRepOrd(var v: TVetor; n: Integer): Integer;
var
  i, j: Integer;
begin
  if n = 0 then
  begin
    elimRepOrd := 0;
    Exit;
  end;
  j := 0;
  for i := 1 to n - 1 do
    if v[i] <> v[j] then
    begin
      Inc(j);
      v[j] := v[i];
    end;
  elimRepOrd := j + 1;
end;

var
  v: TVetor;
  n, i, novoN: Integer;
begin
  n := 10;
  v[0] := 1; v[1] := 1; v[2] := 2; v[3] := 2; v[4] := 2;
  v[5] := 3; v[6] := 3; v[7] := 4; v[8] := 4; v[9] := 5;
  novoN := elimRepOrd(v, n);
  Write('Vetor resultante (sem repetições): ');
  for i := 0 to novoN - 1 do
    Write(v[i], ' ');
  Writeln;
  Writeln('Número de elementos distintos: ', novoN);
end.
