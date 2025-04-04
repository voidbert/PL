program Ex50;

type
  Posicao = record
    x, y: Integer;
  end;

function vizinhos(p: Posicao; pos: array of Posicao; N: Integer): Integer;
var
  i, count, dx, dy: Integer;
begin
  count := 0;
  for i := 0 to N - 1 do
  begin
    if (p.x = pos[i].x) and (p.y = pos[i].y) then
      continue;
    dx := p.x - pos[i].x;
    if dx < 0 then dx := -dx;
    dy := p.y - pos[i].y;
    if dy < 0 then dy := -dy;
    if (dx <= 1) and (dy <= 1) then
      Inc(count);
  end;
  vizinhos := count;
end;

var
  posicoes: array[0..5] of Posicao;
  p: Posicao;
  numVizinhos: Integer;
  i: Integer;
begin
  posicoes[0].x := 2; posicoes[0].y := 3;
  posicoes[1].x := 3; posicoes[1].y := 3;
  posicoes[2].x := 1; posicoes[2].y := 2;
  posicoes[3].x := 2; posicoes[3].y := 4;
  posicoes[4].x := 4; posicoes[4].y := 3;
  posicoes[5].x := 2; posicoes[5].y := 2;

  p.x := 2;
  p.y := 3;

  numVizinhos := vizinhos(p, posicoes, 6);
  WriteLn('Número de posições adjacentes a (', p.x, ', ', p.y, '): ', numVizinhos);
end.
