program Ex14;

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

function charMaisfreq(s: TString): char;
var
  freq: array[0..255] of integer;
  i, len, maxFreq, maxIndex: integer;
begin
  len := StrLen(s);
  if len = 0 then
  begin
    charMaisfreq := #0;
    Exit;
  end;
  for i := 0 to 255 do
    freq[i] := 0;
  for i := 1 to len do
    freq[ord(s[i])] := freq[ord(s[i])] + 1;
  maxFreq := -1;
  maxIndex := 0;
  for i := 0 to 255 do
    if freq[i] > maxFreq then
    begin
      maxFreq := freq[i];
      maxIndex := i;
    end;
  charMaisfreq := chr(maxIndex);
end;

var
  s: TString;
  i: integer;
  c: char;
begin
  for i := 1 to 255 do s[i] := #0;
  s[1] := 'a'; s[2] := 'b'; s[3] := 'r'; s[4] := 'a';
  s[5] := 'c'; s[6] := 'a'; s[7] := 'd'; s[8] := 'a';
  s[9] := 'b'; s[10] := 'r'; s[11] := 'a'; s[12] := #0;
  c := charMaisfreq(s);
  if c = #0 then
    writeln('String vazia.')
  else
    writeln('Caractere mais frequente: ', c);
end.
