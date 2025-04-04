program Ex26;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

procedure insere(var v: TVetor; var N: Integer; x: Integer);
var
  i, pos: Integer;
begin
  pos := N;
  for i := 0 to N - 1 do
    if v[i] > x then
    begin
      pos := i;
      Break;
    end;
  for i := N downto pos + 1 do
    v[i] := v[i-1];
  v[pos] := x;
  Inc(N);
end;

var
  v: TVetor;
  N, i, x: Integer;
begin
  N := 5;
  v[0] := 1; v[1] := 3; v[2] := 5; v[3] := 7; v[4] := 9;
  Write('Insere o valor a adicionar: ');
  Readln(x);
  insere(v, N, x);
  Write('Vetor resultante: ');
  for i := 0 to N - 1 do
    Write(v[i], ' ');
  Writeln;
end.
