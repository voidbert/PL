program Ex17;

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

function maiorPrefixo(s1, s2: TString): integer;
var
  i, len1, len2: integer;
begin
  len1 := StrLen(s1);
  len2 := StrLen(s2);
  i := 1;
  while (i <= len1) and (i <= len2) and (s1[i] = s2[i]) do
    i := i + 1;
  maiorPrefixo := i - 1;
end;

var
  s1, s2: TString;
  i: integer;
  res: integer;
begin
  for i := 1 to 255 do
  begin
    s1[i] := #0;
    s2[i] := #0;
  end;
  s1[1] := 'a'; s1[2] := 'b'; s1[3] := 'c'; s1[4] := 'd'; s1[5] := 'e'; s1[6] := 'f'; s1[7] := #0;
  s2[1] := 'a'; s2[2] := 'b'; s2[3] := 'c'; s2[4] := 'X'; s2[5] := 'Y'; s2[6] := 'Z'; s2[7] := #0;
  res := maiorPrefixo(s1, s2);
  writeln('Maior prefixo comum tem comprimento: ', res);
end.
