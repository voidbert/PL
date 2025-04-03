program Ex38;
const
  MAX = 100;
type
  TVetor = array[0..MAX-1] of Integer;

procedure somasAc(v: TVetor; var Ac: TVetor; N: Integer);
var
  i, soma: Integer;
begin
  soma := 0;
  for i := 0 to N - 1 do
  begin
    soma := soma + v[i];
    Ac[i] := soma;
  end;
end;

var
  v, Ac: TVetor;
  N, i: Integer;
begin
  N := 5;
  v[0] := 2; v[1] := 4; v[2] := 6; v[3] := 8; v[4] := 10;
  somasAc(v, Ac, N);
  Write('Vetor de somas acumuladas: ');
  for i := 0 to N - 1 do
    Write(Ac[i], ' ');
  Writeln;
end.
