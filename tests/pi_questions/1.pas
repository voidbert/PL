program Ex1;
var
  num, maior: Integer;
begin
  maior := -MaxInt;
  writeln('Insere números (termina com 0):');
  repeat
    read(num);
    if num <> 0 then
      if num > maior then
        maior := num;
  until num = 0;
  if maior = -MaxInt then
    writeln('Nenhum número foi inserido.')
  else
    writeln('O maior número é: ', maior);
end.
