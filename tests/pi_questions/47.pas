program Ex47;

const
  MAX_MOV = 100;

type
  Movimento = (Norte, Oeste, Sul, Este);
  TMovimentos = array[1..MAX_MOV] of Movimento;
  Posicao = record
    x, y: Integer;
  end;

function posFinal(inicial: Posicao; mov: TMovimentos; N: Integer): Posicao;
var
  i: Integer;
  resultado: Posicao;
begin
  resultado := inicial;
  for i := 1 to N do
    case mov[i] of
      Norte: Inc(resultado.y);
      Sul:   Dec(resultado.y);
      Este:  Inc(resultado.x);
      Oeste: Dec(resultado.x);
    end;
  posFinal := resultado;
end;

var
  inicial, finalPos: Posicao;
  mov: TMovimentos;
  N, i: Integer;
begin
  inicial.x := 0;
  inicial.y := 0;
  N := 5;

  mov[1] := Norte;
  mov[2] := Norte;
  mov[3] := Este;
  mov[4] := Sul;
  mov[5] := Oeste;

  finalPos := posFinal(inicial, mov, N);
  WriteLn('Posição final: (', finalPos.x, ', ', finalPos.y, ')');
end.
