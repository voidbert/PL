program Ex19;

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

function sufPref(s1, s2: TString): integer;
var
  len1, len2, k, i: integer;
  match: boolean;
begin
  len1 := StrLen(s1);
  len2 := StrLen(s2);
  sufPref := 0;
  for k := len1 downto 1 do
  begin
    if k > len2 then
      continue;
    match := true;
    for i := 1 to k do
      if s1[len1 - k + i] <> s2[i] then
      begin
        match := false;
        break;
      end;
    if match then
    begin
      sufPref := k;
      exit;
    end;
  end;
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
  s1[1] := 'b'; s1[2] := 'a'; s1[3] := 't'; s1[4] := 'o'; s1[5] := 't'; s1[6] := 'a'; s1[7] := #0;
  s2[1] := 't'; s2[2] := 'o'; s2[3] := 't'; s2[4] := 'a'; s2[5] := 'l'; s2[6] := 'i';
  s2[7] := 'd'; s2[8] := 'a'; s2[9] := 'd'; s2[10] := 'e'; s2[11] := #0;
  res := sufPref(s1, s2);
  writeln('Maior sufixo de s1 que é prefixo de s2 tem comprimento: ', res);
end.
