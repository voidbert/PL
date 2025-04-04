program Ex41;
const
  MAXN = 10;
  MAXM = 10;
type
  TMatrix = array[0..MAXN-1, 0..MAXM-1] of Integer;

procedure addTo(N, M: Integer; var a: TMatrix; b: TMatrix);
var
  i, j: Integer;
begin
  for i := 0 to N - 1 do
    for j := 0 to M - 1 do
      a[i][j] := a[i][j] + b[i][j];
end;

var
  a, b: TMatrix;
  N, M, i, j: Integer;
begin
  N := 2; M := 3;
  a[0][0] := 1; a[0][1] := 2; a[0][2] := 3;
  a[1][0] := 4; a[1][1] := 5; a[1][2] := 6;

  b[0][0] := 6; b[0][1] := 5; b[0][2] := 4;
  b[1][0] := 3; b[1][1] := 2; b[1][2] := 1;

  addTo(N, M, a, b);

  Writeln('Matriz a após a soma: ');
  for i := 0 to N - 1 do
  begin
    for j := 0 to M - 1 do
      Write(a[i][j]:4, ' ');
    Writeln;
  end;
end.
