program Ex18;

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

function maiorSufixo(s1, s2: TString): integer;
var
  len1, len2, count: integer;
begin
  len1 := StrLen(s1);
  len2 := StrLen(s2);
  count := 0;
  while (count < len1) and (count < len2) and (s1[len1 - count] = s2[len2 - count]) do
    count := count + 1;
  maiorSufixo := count;
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
  s1[1] := 'p'; s1[2] := 'r'; s1[3] := 'o'; s1[4] := 'g'; s1[5] := 'r';
  s1[6] := 'a'; s1[7] := 'm'; s1[8] := 'a'; s1[9] := #0;
  s2[1] := 'a'; s2[2] := 'n'; s2[3] := 'i'; s2[4] := 'm'; s2[5] := 'a'; s2[6] := #0;
  res := maiorSufixo(s1, s2);
  writeln('Maior sufixo comum tem comprimento: ', res);
end.
