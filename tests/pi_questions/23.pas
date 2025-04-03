program Ex23;

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

function palindorome(s: TString): integer;
var
  len, i: integer;
begin
  len := StrLen(s);
  for i := 1 to len div 2 do
    if s[i] <> s[len - i + 1] then
    begin
      palindorome := 0;
      exit;
    end;
  palindorome := 1;
end;

var
  s: TString;
  i: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'r'; s[2] := 'a'; s[3] := 'd'; s[4] := 'a'; s[5] := 'r'; s[6] := #0;

  if palindorome(s) = 1 then
    writeln('A palavra é palíndroma.')
  else
    writeln('A palavra não é palíndroma.');
end.
