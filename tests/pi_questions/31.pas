program Ex31;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function maisFreq(const v: TVetor; N: Integer): Integer;
var
  i, current, count, maxCount, resultVal: Integer;
begin
  if N = 0 then
  begin
    maisFreq := 0;
    Exit;
  end;
  maxCount := 0;
  i := 0;
  while i < N do
  begin
    current := v[i];
    count := 0;
    while (i < N) and (v[i] = current) do
    begin
      Inc(count);
      Inc(i);
    end;
    if count > maxCount then
    begin
      maxCount := count;
      resultVal := current;
    end;
  end;
  maisFreq := resultVal;
end;

var
  v: TVetor;
  N, result: Integer;
begin
  N := 10;
  v[0] := 2; v[1] := 2; v[2] := 2; v[3] := 3; v[4] := 3;
  v[5] := 4; v[6] := 4; v[7] := 4; v[8] := 4; v[9] := 5;
  result := maisFreq(v, N);
  Writeln('Elemento mais frequente: ', result);
end.
