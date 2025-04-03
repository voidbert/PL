program Ex2;
var
  num, soma, count: Integer;
  media: Real;
begin
  soma := 0;
  count := 0;
  writeln('Insere números (termina com 0):');
  repeat
    read(num);
    if num <> 0 then
    begin
      soma := soma + num;
      count := count + 1;
    end;
  until num = 0;

  if count = 0 then
    writeln('Nenhum número foi inserido.')
  else
  begin
    media := soma / count;
    writeln('A média da sequência é: ', media:0:2);
  end;
end.
