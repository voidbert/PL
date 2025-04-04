program Ex33;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function elimRep(var v: TVetor; n: Integer): Integer;
var
  i, j, k: Integer;
  achou: Boolean;
begin
  if n = 0 then
  begin
    elimRep := 0;
    Exit;
  end;
  j := 0;
  for i := 0 to n - 1 do
  begin
    achou := False;
    for k := 0 to j - 1 do
      if v[k] = v[i] then
      begin
        achou := True;
        Break;
      end;
    if not achou then
    begin
      v[j] := v[i];
      Inc(j);
    end;
  end;
  elimRep := j;
end;

var
  v: TVetor;
  n, novoN, i: Integer;
begin
  n := 10;
  v[0] := 1; v[1] := 2; v[2] := 2; v[3] := 3; v[4] := 1;
  v[5] := 4; v[6] := 4; v[7] := 5; v[8] := 3; v[9] := 2;
  novoN := elimRep(v, n);
  Write('Vetor resultante sem repetições: ');
  for i := 0 to novoN - 1 do
    Write(v[i], ' ');
  Writeln;
  Writeln('Número de elementos distintos: ', novoN);
end.
