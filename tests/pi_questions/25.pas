program Ex25;

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

procedure PrintString(const s: TString);
var
  i: integer;
begin
  i := 1;
  while (i <= 255) and (s[i] <> #0) do
  begin
    write(s[i]);
    i := i + 1;
  end;
end;

function limpaEspacos(var t: TString): integer;
var
  i, j, len: integer;
begin
  len := StrLen(t);
  j := 1;
  i := 1;
  while i <= len do
  begin
    t[j] := t[i];
    if t[i] = ' ' then
      while (i < len) and (t[i+1] = ' ') do
        i := i + 1;
    j := j + 1;
    i := i + 1;
  end;
  if j <= 255 then
    t[j] := #0;
  limpaEspacos := j - 1;
end;

var
  s: TString;
  i, newLen: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'l'; s[2] := 'i'; s[3] := 'b'; s[4] := 'e'; s[5] := 'r';
  s[6] := 'd'; s[7] := 'a'; s[8] := 'd'; s[9] := 'e'; s[10] := ',';
  s[11] := ' '; s[12] := ' '; s[13] := 'i'; s[14] := 'g'; s[15] := 'u';
  s[16] := 'a'; s[17] := 'l'; s[18] := 'd'; s[19] := 'a'; s[20] := 'd';
  s[21] := 'e'; s[22] := ' '; s[23] := ' '; s[24] := ' '; s[25] := 'e';
  s[26] := ' '; s[27] := 'f'; s[28] := 'r'; s[29] := 'a'; s[30] := 't';
  s[31] := 'e'; s[32] := 'r'; s[33] := 'n'; s[34] := 'i'; s[35] := 'd';
  s[36] := 'a'; s[37] := 'd'; s[38] := 'e'; s[39] := #0;

  write('Antes: ');
  PrintString(s);
  writeln;
  newLen := limpaEspacos(s);
  write('Depois: ');
  PrintString(s);
  writeln;
  writeln('Novo comprimento: ', newLen);
end.
