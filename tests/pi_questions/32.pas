program Ex32;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function maxCresc(const v: TVetor; N: Integer): Integer;
var
  i, current, maxSeq: Integer;
begin
  if N = 0 then
  begin
    maxCresc := 0;
    Exit;
  end;
  current := 1;
  maxSeq := 1;
  for i := 1 to N - 1 do
  begin
    if v[i] > v[i - 1] then
      Inc(current)
    else
      current := 1;
    if current > maxSeq then
      maxSeq := current;
  end;
  maxCresc := maxSeq;
end;

var
  v: TVetor;
  N, i, result: Integer;
begin
  N := 10;
  v[0] := 1; v[1] := 2; v[2] := 3; v[3] := 2; v[4] := 1;
  v[5] := 4; v[6] := 10; v[7] := 12; v[8] := 5; v[9] := 4;
  result := maxCresc(v, N);
  Writeln('Comprimento da maior sequência crescente: ', result);
end.
