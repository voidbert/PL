program Ex44;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function intersectMSet(N: Integer; v1, v2: TVetor; var r: TVetor): Integer;
var
  i, total: Integer;
begin
  total := 0;
  for i := 0 to N - 1 do
  begin
    if v1[i] < v2[i] then
      r[i] := v1[i]
    else
      r[i] := v2[i];
    total := total + r[i];
  end;
  intersectMSet := total;
end;

var
  v1, v2, r: TVetor;
  N, i, total: Integer;
begin
  N := 8;

  v1[0] := 0; v1[1] := 2; v1[2] := 0; v1[3] := 0;
  v1[4] := 1; v1[5] := 0; v1[6] := 0; v1[7] := 3;

  v2[0] := 0; v2[1] := 1; v2[2] := 0; v2[3] := 1;
  v2[4] := 2; v2[5] := 0; v2[6] := 0; v2[7] := 2;

  total := intersectMSet(N, v1, v2, r);

  Write('Intersecção (array r): ');
  for i := 0 to N - 1 do
    Write(r[i], ' ');
  Writeln;
  Writeln('Total de elementos na intersecção: ', total);
end.
