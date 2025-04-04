program Ex30;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function menosFreq(const v: TVetor; N: Integer): Integer;
var
  i, current, count, minCount, resultVal: Integer;
begin
  if N = 0 then
  begin
    menosFreq := 0;
    Exit;
  end;
  minCount := MaxInt;
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
    if count < minCount then
    begin
      minCount := count;
      resultVal := current;
    end;
  end;
  menosFreq := resultVal;
end;

var
  v: TVetor;
  N, result: Integer;
begin
  N := 10;
  v[0] := 1; v[1] := 1; v[2] := 2; v[3] := 3; v[4] := 3;
  v[5] := 3; v[6] := 4; v[7] := 4; v[8] := 5; v[9] := 5;
  result := menosFreq(v, N);
  Writeln('Elemento menos frequente: ', result);
end.
