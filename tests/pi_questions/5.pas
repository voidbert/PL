program Ex5;

var
  n: Cardinal;

function trailingZ(n: Cardinal): Integer;
var
  count: Integer;
begin
  count := 0;
  while (n <> 0) and ((n and 1) = 0) do
  begin
    if (n mod 2) = 0 then
      count := count + 1;
    n := n div 2;
  end;
  trailingZ := count;
end;

begin
  Write('Insira um número inteiro sem sinal: ');
  ReadLn(n);
  WriteLn('Número de trailing zeros: ', trailingZ(n));
end.
