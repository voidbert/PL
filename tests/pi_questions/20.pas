program Ex20;

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

function contaPal(s: TString): integer;
var
  i, len, count: integer;
  inWord: boolean;
begin
  len := StrLen(s);
  count := 0;
  inWord := false;
  for i := 1 to len do
  begin
    if s[i] <> ' ' then
    begin
      if not inWord then
      begin
        inWord := true;
        count := count + 1;
      end;
    end
    else
      inWord := false;
  end;
  contaPal := count;
end;

var
  s: TString;
  i: integer;
  res: integer;
begin
  for i := 1 to 255 do
    s[i] := #0;
  s[1] := 'a'; s[2] := ' '; s[3] := 'a'; s[4] := ' ';
  s[5] := 'b'; s[6] := 'b'; s[7] := ' '; s[8] := 'a'; s[9] := #0;
  res := contaPal(s);
  writeln('Número de palavras: ', res);
end.
