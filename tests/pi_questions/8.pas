program Ex8;
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

function myStrCpy(var dest: TString; const source: TString): TString;
var
  i: integer;
begin
  for i := 1 to 255 do
    dest[i] := source[i];
  myStrCpy := dest;
end;

var
  source, dest: TString;
  i: integer;
begin
  for i := 1 to 255 do
  begin
    source[i] := #0;
    dest[i] := #0;
  end;

  source[1] := 'E'; source[2] := 'x'; source[3] := 'e'; source[4] := 'm';
  source[5] := 'p'; source[6] := 'l'; source[7] := 'o'; source[8] := ' ';
  source[9] := 'd'; source[10] := 'e'; source[11] := ' ';
  source[12] := 'c'; source[13] := 'o'; source[14] := 'p'; source[15] := 'i';
  source[16] := 'a'; source[17] := #0;

  myStrCpy(dest, source);
  write('Source: ');
  PrintString(source);
  writeln;
  write('Dest: ');
  PrintString(dest);
  writeln;
end.
