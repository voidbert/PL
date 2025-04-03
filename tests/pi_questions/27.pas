program Ex27;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

procedure merge(const a, b: TVetor; na, nb: Integer; var r: TVetor);
var
  i, j, k: Integer;
begin
  i := 0; j := 0; k := 0;
  while (i < na) and (j < nb) do
  begin
    if a[i] <= b[j] then
    begin
      r[k] := a[i];
      Inc(i);
    end
    else
    begin
      r[k] := b[j];
      Inc(j);
    end;
    Inc(k);
  end;
  while i < na do
  begin
    r[k] := a[i];
    Inc(i);
    Inc(k);
  end;
  while j < nb do
  begin
    r[k] := b[j];
    Inc(j);
    Inc(k);
  end;
end;

var
  a, b, r: TVetor;
  na, nb, i: Integer;
begin
  na := 5; nb := 4;
  a[0] := 1; a[1] := 3; a[2] := 5; a[3] := 7; a[4] := 9;
  b[0] := 2; b[1] := 4; b[2] := 6; b[3] := 8;
  merge(a, b, na, nb, r);
  Write('Vetor resultante: ');
  for i := 0 to na + nb - 1 do
    Write(r[i], ' ');
  Writeln;
end.
