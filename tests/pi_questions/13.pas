program Ex13;

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

procedure truncW(var t: TString; n: integer);
var
  i, len, resIndex, wordCount: integer;
  res: TString;
begin
  for i := 1 to 255 do
    res[i] := #0;
  resIndex := 1;
  i := 1;
  len := StrLen(t);
  while i <= len do
  begin
    if t[i] = ' ' then
    begin
      if (resIndex = 1) then
      begin
        { nothing }
      end
      else if res[resIndex - 1] <> ' ' then
      begin
        res[resIndex] := ' ';
        resIndex := resIndex + 1;
      end;
      while (i <= len) and (t[i] = ' ') do
        i := i + 1;
    end
    else
    begin
      wordCount := 0;
      while (i <= len) and (t[i] <> ' ') do
      begin
        if wordCount < n then
        begin
          res[resIndex] := t[i];
          resIndex := resIndex + 1;
          wordCount := wordCount + 1;
        end;
        i := i + 1;
      end;
    end;
  end;
  if resIndex <= 255 then
    res[resIndex] := #0;
  t := res;
end;

var
  t: TString;
  i: integer;
begin
  for i := 1 to 255 do t[i] := #0;
  t[1] := 'l'; t[2] := 'i'; t[3] := 'b'; t[4] := 'e'; t[5] := 'r';
  t[6] := 'd'; t[7] := 'a'; t[8] := 'd'; t[9] := 'e'; t[10] := ',';
  t[11] := ' '; t[12] := ' '; t[13] := 'i'; t[14] := 'g'; t[15] := 'u';
  t[16] := 'a'; t[17] := 'l'; t[18] := 'd'; t[19] := 'a'; t[20] := 'd';
  t[21] := 'e'; t[22] := ' '; t[23] := ' '; t[24] := ' '; t[25] := 'e';
  t[26] := ' '; t[27] := 'f'; t[28] := 'r'; t[29] := 'a'; t[30] := 't';
  t[31] := 'e'; t[32] := 'r'; t[33] := 'n'; t[34] := 'i'; t[35] := 'd';
  t[36] := 'a'; t[37] := 'd'; t[38] := 'e'; t[39] := #0;
  write('Antes: '); PrintString(t); writeln;
  truncW(t, 4);
  write('Depois: '); PrintString(t); writeln;
end.
