program Ex49;

type
  Posicao = record
    x, y: Integer;
  end;

function maisCentral(pos: array of Posicao; N: Integer): Integer;
var
  i, indiceCentral: Integer;
  dist, menorDist: LongInt;
begin
  if N = 0 then
  begin
    maisCentral := -1;
    Exit;
  end;
  indiceCentral := 0;
  menorDist := pos[0].x * pos[0].x + pos[0].y * pos[0].y;
  for i := 1 to N - 1 do
  begin
    dist := pos[i].x * pos[i].x + pos[i].y * pos[i].y;
    if dist < menorDist then
    begin
      menorDist := dist;
      indiceCentral := i;
    end;
  end;
  maisCentral := indiceCentral;
end;

var
  posicoes: array[0..4] of Posicao;
  indice: Integer;
begin
  posicoes[0].x := 3; posicoes[0].y := 4;
  posicoes[1].x := 1; posicoes[1].y := 1;
  posicoes[2].x := -2; posicoes[2].y := 2;
  posicoes[3].x := 5; posicoes[3].y := 0;
  posicoes[4].x := 0; posicoes[4].y := 0;

  indice := maisCentral(posicoes, 5);
  WriteLn('A posição mais central é a de índice: ', indice);
  WriteLn('Coordenadas: (', posicoes[indice].x, ', ', posicoes[indice].y, ')');
end.
