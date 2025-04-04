program Ex40;
const
  MAX = 10;
type
  TMatrix = array[0..MAX-1, 0..MAX-1] of Real;

procedure transposta(N: Integer; var m: TMatrix);
var
  i, j: Integer;
  temp: Real;
begin
  for i := 0 to N - 1 do
    for j := i + 1 to N - 1 do
    begin
      temp := m[i][j];
      m[i][j] := m[j][i];
      m[j][i] := temp;
    end;
end;

var
  m: TMatrix;
  N, i, j: Integer;
begin
  N := 3;
  m[0][0] := 1; m[0][1] := 2; m[0][2] := 3;
  m[1][0] := 4; m[1][1] := 5; m[1][2] := 6;
  m[2][0] := 7; m[2][1] := 8; m[2][2] := 9;

  transposta(N, m);
  Writeln('Matriz transposta: ');
  for i := 0 to N - 1 do
  begin
    for j := 0 to N - 1 do
      Write(m[i][j]:4:0, ' ');
    Writeln;
  end;
end.
