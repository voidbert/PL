program Ex43;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function intersectSet(N: Integer; v1, v2: TVetor; var r: TVetor): Integer;
var
  i, count: Integer;
begin
  count := 0;
  for i := 0 to N - 1 do
  begin
    if (v1[i] = 1) and (v2[i] = 1) then
    begin
      r[i] := 1;
      Inc(count);
    end
    else
      r[i] := 0;
  end;
  intersectSet := count;
end;

var
  N, i, res: Integer;
  v1, v2, r: TVetor;
begin
  N := 8;
  v1[0] := 0; v1[1] := 1; v1[2] := 0; v1[3] := 0;
  v1[4] := 1; v1[5] := 0; v1[6] := 0; v1[7] := 1;

  v2[0] := 0; v2[1] := 0; v2[2] := 0; v2[3] := 0;
  v2[4] := 1; v2[5] := 0; v2[6] := 0; v2[7] := 1;

  res := intersectSet(N, v1, v2, r);
  Write('Intersecção dos conjuntos (array r): ');
  for i := 0 to N - 1 do
    Write(r[i], ' ');
  Writeln;
  Writeln('Número de elementos na intersecção: ', res);
end.
