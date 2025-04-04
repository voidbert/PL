program Ex24;

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

function remRep(var x: TString): integer;
var
  i, j, len: integer;
begin
  len := StrLen(x);
  if len = 0 then
  begin
    remRep := 0;
    exit;
  end;
  j := 1;
  for i := 2 to len do
    if x[i] <> x[j] then
    begin
      j := j + 1;
      x[j] := x[i];
    end;
  if j < 255 then
    x[j+1] := #0;
  remRep := j;
end;

var
  s: TString;
  i, newLen: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'a'; s[2] := 'a'; s[3] := 'a';
  s[4] := 'b'; s[5] := 'a'; s[6] := 'a'; s[7] := 'a';
  s[8] := 'a'; s[9] := 'b'; s[10] := 'b'; s[11] := 'b';
  s[12] := 'a'; s[13] := 'a'; s[14] := 'a'; s[15] := #0;

  newLen := remRep(s);
  write('String resultante: ');
  PrintString(s);
  writeln;
  writeln('Novo comprimento: ', newLen);
end.
