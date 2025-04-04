program Ex12;

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

procedure strnoV(var s: TString);
var
  i, j, len: integer;
  res: TString;
begin
  for i := 1 to 255 do
    res[i] := #0;
  j := 1;
  len := StrLen(s);
  for i := 1 to len do
    if not (s[i] in ['a','e','i','o','u','A','E','I','O','U']) then
    begin
      if j <= 255 then
      begin
        res[j] := s[i];
        j := j + 1;
      end;
    end;
  if j <= 255 then
    res[j] := #0;
  s := res;
end;

var
  s: TString;
  i: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'P'; s[2] := 'r'; s[3] := 'o'; s[4] := 'g'; s[5] := 'r';
  s[6] := 'a'; s[7] := 'm'; s[8] := 'a'; s[9] := 'c'; s[10] := 'a';
  s[11] := 'o'; s[12] := #0;
  write('Original: '); PrintString(s); writeln;
  strnoV(s);
  write('Sem vogais: '); PrintString(s); writeln;
end.
