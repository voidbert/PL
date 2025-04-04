program Ex9;
type
  TString = packed array[1..255] of char;

function myStrCmp(const s1, s2: TString): Integer;
var
  i: integer;
begin
  i := 1;
  while (i <= 255) and (s1[i] <> #0) and (s2[i] <> #0) and (s1[i] = s2[i]) do
    i := i + 1;
  if (i > 255) then
    myStrCmp := 0
  else
    myStrCmp := Ord(s1[i]) - Ord(s2[i]);
end;

var
  s1, s2: TString;
  i: integer;
  cmp: integer;
begin
  for i := 1 to 255 do
  begin
    s1[i] := #0;
    s2[i] := #0;
  end;
  s1[1] := 'a'; s1[2] := 'b'; s1[3] := 'c'; s1[4] := #0;
  s2[1] := 'a'; s2[2] := 'b'; s2[3] := 'd'; s2[4] := #0;

  cmp := myStrCmp(s1, s2);
  WriteLn('Resultado da comparação: ', cmp);
end.
