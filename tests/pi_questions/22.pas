program Ex22;

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

function contida(a, b: TString): integer;
var
  i, j, lenA, lenB: integer;
  found: boolean;
begin
  lenA := StrLen(a);
  lenB := StrLen(b);
  for i := 1 to lenA do
  begin
    found := false;
    for j := 1 to lenB do
      if a[i] = b[j] then
      begin
        found := true;
        break;
      end;
    if not found then
    begin
      contida := 0;
      Exit;
    end;
  end;
  contida := 1;
end;

var
  a, b: TString;
  i: integer;
  res: integer;
begin
  for i := 1 to 255 do
  begin
    a[i] := #0;
    b[i] := #0;
  end;
  a[1] := 'b'; a[2] := 'r'; a[3] := 'a'; a[4] := 'g'; a[5] := 'a'; a[6] := #0;
  b[1] := 'b'; b[2] := 'r'; b[3] := 'a'; b[4] := 'c'; b[5] := 'a'; b[6] := 'r';
  b[7] := 'a'; b[8] := ' '; b[9] := 'a'; b[10] := 'u'; b[11] := 'g';
  b[12] := 'u'; b[13] := 's'; b[14] := 't'; b[15] := 'a'; b[16] := #0;
  res := contida(a, b);
  writeln('Contida (braga em bracara augusta): ', res);

  a[1] := 'b'; a[2] := 'r'; a[3] := 'a'; a[4] := 'g'; a[5] := 'a'; a[6] := #0;
  b[1] := 'b'; b[2] := 'r'; b[3] := 'a'; b[4] := 'c'; b[5] := 'a'; b[6] := 'r';
  b[7] := 'e'; b[8] := 'n'; b[9] := 's'; b[10] := 'e'; b[11] := #0;
  res := contida(a, b);
  writeln('Contida (braga em bracarense): ', res);
end.
