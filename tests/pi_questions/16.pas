program Ex16;

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

function difConsecutivos(s: TString): integer;
var
  i, len, atual, maximo: integer;
begin
  len := StrLen(s);
  if len = 0 then
  begin
    difConsecutivos := 0;
    Exit;
  end;
  atual := 1;
  maximo := 1;
  for i := 2 to len do
  begin
    if s[i] <> s[i-1] then
      atual := atual + 1
    else
      atual := 1;
    if atual > maximo then
      maximo := atual;
  end;
  difConsecutivos := maximo;
end;

var
  s: TString;
  i: integer;
  res: integer;
begin
  for i := 1 to 255 do s[i] := #0;
  s[1] := 'a'; s[2] := 'a'; s[3] := 'b'; s[4] := 'c';
  s[5] := 'c'; s[6] := 'c'; s[7] := 'a'; s[8] := 'a';
  s[9] := 'c'; s[10] := #0;
  res := difConsecutivos(s);
  writeln('Maior sequência de diferentes: ', res);
end.
