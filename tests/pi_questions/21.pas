program Ex21;

type
  TString = packed array[1..255] of char;

function StrLen(const s: TString): integer;
var
  i: integer;
begin
  i := 1;
  while (i <= 255) and (s[i] <> #0) do
    i := i + 1;
  StrLen := i - 1;
end;

function contaVogais(s: TString): integer;
var
  i, len, count: integer;
begin
  len := StrLen(s);
  count := 0;
  for i := 1 to len do
    if s[i] in ['a','e','i','o','u','A','E','I','O','U'] then
      count := count + 1;
  contaVogais := count;
end;

var
  s: TString;
  i: integer;
  res: integer;
begin
  for i := 1 to 255 do s[i] := #0;
  s[1] := 'P'; s[2] := 'r'; s[3] := 'o'; s[4] := 'g'; s[5] := 'r';
  s[6] := 'a'; s[7] := 'm'; s[8] := 'a'; s[9] := 'c'; s[10] := 'a';
  s[11] := 'o'; s[12] := #0;
  res := contaVogais(s);
  writeln('Número de vogais: ', res);
end.
