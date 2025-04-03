program Ex3;
var
  num, maior, segMaior: Integer;
begin
  maior := -MaxInt;
  segMaior := -MaxInt;
  writeln('Insere números (termina com 0):');
  repeat
    read(num);
    if num <> 0 then
    begin
      if num > maior then
      begin
        segMaior := maior;
        maior := num;
      end
      else if (num > segMaior) and (num <> maior) then
        segMaior := num;
    end;
  until num = 0;

  if segMaior = -MaxInt then
    writeln('Não foi possível determinar o segundo maior (poucos números ou repetidos).')
  else
    writeln('O segundo maior número é: ', segMaior);
end.
