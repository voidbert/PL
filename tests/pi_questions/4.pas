program Ex4;
var
  n: LongInt;

function bitsUm(n: LongInt): Integer;
var
  count: Integer;
begin
  count := 0;
  while n <> 0 do
  begin
    if (n mod 2) = 1 then
      count := count + 1;
    n := n div 2;
  end;
  bitsUm := count;
end;

begin
  Write('Insira um número inteiro sem sinal: ');
  ReadLn(n);
  WriteLn('Número de bits a 1: ', bitsUm(n));
end.
