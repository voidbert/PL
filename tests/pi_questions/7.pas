program Ex7;
type
  TString = packed array[1..255] of char;

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

function myStrCat(var s1: TString; const s2: TString): TString;
var
  i, len1, j: integer;
  resultStr: TString;
begin
  len1 := 0;
  for i := 1 to 255 do
  begin
    if s1[i] = #0 then
      break;
    len1 := len1 + 1;
  end;

  for i := 1 to len1 do
    resultStr[i] := s1[i];

  j := 1;
  while (len1 < 255) and (j <= 255) and (s2[j] <> #0) do
  begin
    resultStr[len1+1] := s2[j];
    len1 := len1 + 1;
    j := j + 1;
  end;
  if len1 < 255 then
    resultStr[len1+1] := #0;
  myStrCat := resultStr;
end;

var
  s1, s2, resultStr: TString;
  i: integer;
begin
  for i := 1 to 255 do
  begin
    s1[i] := #0;
    s2[i] := #0;
  end;
  s1[1] := 'H'; s1[2] := 'e'; s1[3] := 'l'; s1[4] := 'l';
  s1[5] := 'o'; s1[6] := ','; s1[7] := ' '; s1[8] := #0;
  s2[1] := 'W'; s2[2] := 'o'; s2[3] := 'r'; s2[4] := 'l';
  s2[5] := 'd'; s2[6] := '!'; s2[7] := #0;

  write('Antes: ');
  PrintString(s1);
  writeln;

  resultStr := myStrCat(s1, s2);

  write('Depois: ');
  PrintString(resultStr);
  writeln;
end.
