program Ex6;
var
  n: Cardinal;

function qDig(n: Cardinal): Integer;
var
  count: Integer;
begin
  if n = 0 then
    qDig := 1
  else
  begin
    count := 0;
    while n <> 0 do
    begin
      count := count + 1;
      n := n div 10;
    end;
    qDig := count;
  end;
end;

begin
  Write('Insira um número inteiro sem sinal: ');
  ReadLn(n);
  WriteLn('Número de dígitos: ', qDig(n));
end.
