program Ex11;

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

procedure strrev(var s: TString);
var
  i, len: integer;
  temp: char;
begin
  len := StrLen(s);
  for i := 1 to len div 2 do
  begin
    temp := s[i];
    s[i] := s[len - i + 1];
    s[len - i + 1] := temp;
  end;
end;

var
  s: TString;
  i: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'H'; s[2] := 'e'; s[3] := 'l'; s[4] := 'l'; s[5] := 'o'; s[6] := #0;
  write('Original: '); PrintString(s); writeln;
  strrev(s);
  write('Invertida: '); PrintString(s); writeln;
end.
