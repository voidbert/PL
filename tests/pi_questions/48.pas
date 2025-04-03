program Ex48;

const
  MAX_MOV = 100;

type
  Movimento = (Norte, Oeste, Sul, Este);
  TMovimentos = array[1..MAX_MOV] of Movimento;
  Posicao = record
    x, y: Integer;
  end;

function caminho(inicial, finalPos: Posicao; var mov: TMovimentos; N: Integer): Integer;
var
  dx, dy, total, i, cont: Integer;
begin
  dx := finalPos.x - inicial.x;
  dy := finalPos.y - inicial.y;
  total := Abs(dx) + Abs(dy);
  if total > N then
  begin
    caminho := -1;
    Exit;
  end;
  cont := 0;

  if dy > 0 then
    for i := 1 to dy do
    begin
      Inc(cont);
      mov[cont] := Norte;
    end
  else if dy < 0 then
    for i := 1 to Abs(dy) do
    begin
      Inc(cont);
      mov[cont] := Sul;
    end;

  if dx > 0 then
    for i := 1 to dx do
    begin
      Inc(cont);
      mov[cont] := Este;
    end
  else if dx < 0 then
    for i := 1 to Abs(dx) do
    begin
      Inc(cont);
      mov[cont] := Oeste;
    end;
  caminho := cont;
end;

var
  inicial, finalPos: Posicao;
  mov: TMovimentos;
  numMov, i: Integer;
begin
  inicial.x := 2;
  inicial.y := 3;
  finalPos.x := 5;
  finalPos.y := 6;

  numMov := caminho(inicial, finalPos, mov, MAX_MOV);
  if numMov < 0 then
    WriteLn('Não é possível atingir a posição final com o número máximo de movimentos disponíveis.')
  else
  begin
    WriteLn('Número de movimentos utilizados: ', numMov);
    Write('Sequência de movimentos: ');
    for i := 1 to numMov do
      case mov[i] of
        Norte: Write('Norte ');
        Sul:   Write('Sul ');
        Este:  Write('Este ');
        Oeste: Write('Oeste ');
      end;
    WriteLn;
  end;
end.
