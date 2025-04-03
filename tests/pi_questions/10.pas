program Ex10;
type
  TString = packed array[1..255] of char;

function myStrStr(const s1, s2: TString): Integer;
var
  i, j: integer;
  found: boolean;
begin
  if s2[1] = #0 then
  begin
    myStrStr := 1;
    Exit;
  end;
  for i := 1 to 255 do
  begin
    if s1[i] = #0 then
      break;
    if s1[i] = s2[1] then
    begin
      found := true;
      j := 1;
      while (s2[j] <> #0) do
      begin
        if s1[i+j-1] <> s2[j] then
        begin
          found := false;
          break;
        end;
        j := j + 1;
      end;
      if found then
      begin
        myStrStr := i;
        Exit;
      end;
    end;
  end;
  myStrStr := 0;
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

var
  s1, s2: TString;
  pos: integer;
  i: integer;
begin
  for i := 1 to 255 do
    s1[i] := #0;
  s1[1] := 'E'; s1[2] := 's'; s1[3] := 't'; s1[4] := 'a'; s1[5] := ' ';
  s1[6] := 'e'; s1[7] := ' '; s1[8] := 'u'; s1[9] := 'm'; s1[10] := 'a'; s1[11] := ' ';
  s1[12] := 's'; s1[13] := 't'; s1[14] := 'r'; s1[15] := 'i'; s1[16] := 'n';
  s1[17] := 'g'; s1[18] := ' '; s1[19] := 'd'; s1[20] := 'e'; s1[21] := ' ';
  s1[22] := 'e'; s1[23] := 'x'; s1[24] := 'e'; s1[25] := 'm'; s1[26] := 'p';
  s1[27] := 'l'; s1[28] := 'o'; s1[29] := #0;

  for i := 1 to 255 do
    s2[i] := #0;
  s2[1] := 'e'; s2[2] := 'x'; s2[3] := 'e'; s2[4] := 'm'; s2[5] := 'p';
  s2[6] := 'l'; s2[7] := 'o'; s2[8] := #0;

  pos := myStrStr(s1, s2);
  if pos = 0 then
    WriteLn('Substring não encontrada.')
  else
    WriteLn('Substring encontrada na posição: ', pos);
end.
