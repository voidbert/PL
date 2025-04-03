program Ex46;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function cardinalMSet(N: Integer; v: TVetor): Integer;
var
  i, total: Integer;
begin
  total := 0;
  for i := 0 to N - 1 do
    total := total + v[i];
  cardinalMSet := total;
end;

var
  v: TVetor;
  N, i, total: Integer;
begin
  N := 8;
  v[0] := 0; v[1] := 2; v[2] := 0; v[3] := 0;
  v[4] := 1; v[5] := 0; v[6] := 0; v[7] := 3;

  total := cardinalMSet(N, v);
  Write('Cardinalidade do multi-conjunto: ', total);
  Writeln;
end.
