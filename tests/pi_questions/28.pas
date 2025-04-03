program Ex28;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

function crescente(const a: TVetor; i, j: Integer): Integer;
var
  k: Integer;
begin
  for k := i to j - 1 do
    if a[k] > a[k+1] then
    begin
      crescente := 0;
      Exit;
    end;
  crescente := 1;
end;

var
  a: TVetor;
  i, j, result: Integer;
begin
  a[0] := 1; a[1] := 2; a[2] := 3; a[3] := 2; a[4] := 5;
  i := 0; j := 2;
  result := crescente(a, i, j);
  if result = 1 then
    Writeln('O vetor está ordenado de forma crescente entre as posições ', i, ' e ', j)
  else
    Writeln('O vetor NÃO está ordenado de forma crescente entre as posições ', i, ' e ', j);
end.
