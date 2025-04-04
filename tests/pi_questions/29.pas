program Ex29;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function retiraNeg(var v: TVetor; N: Integer): Integer;
var
  i, j: Integer;
begin
  j := 0;
  for i := 0 to N - 1 do
    if v[i] >= 0 then
    begin
      v[j] := v[i];
      Inc(j);
    end;
  retiraNeg := j;
end;

var
  v: TVetor;
  N, novoN, i: Integer;
begin
  N := 8;
  v[0] := 3; v[1] := -1; v[2] := 4; v[3] := -5; v[4] := 6; v[5] := -2; v[6] := 7; v[7] := 0;
  novoN := retiraNeg(v, N);
  Write('Vetor sem negativos: ');
  for i := 0 to novoN - 1 do
    Write(v[i], ' ');
  Writeln;
  Writeln('Número de elementos não retirados: ', novoN);
end.
