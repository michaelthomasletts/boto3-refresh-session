s = """
lbh orybat gb zr,
naq v, lbh.

jr ner abg jub jr fnl jr ner.
abg jub jr guvax jr ner.
jr ner jub bguref guvax jr ner --
jung bhe npgvbaf fnl jr ner.

fb znxr jung lbh ohvyq frysyrff.
ornhgvshy. ebohfg. cresrpg.

zrqvbpevgl yherf hf sebz qvivavgl.
gur pybfre gb cresrpgvba jr nfpraq,
gur zber fgevqrag rivy tebjf --
orpnhfr rivy pnaabg rkvfg 
vs nyy vf cresrpg.

n guvat vf jung vg vf abg.
n guvat jvgu ab bgure vf abguvat.
naq abguvat
vf gur zbfg cresrpg guvat bs nyy.

ubjrire lbh hfr guvf fbsgjner,
jungrire lbh ohvyq --
znxr vg cresrpg.
qb fb sbe rirelbar ohg lbhefrys.

znl jr or sbetbggra
naq bhe npgvbaf svanyyl fvyrag.
"""


def how(text: str, shift: int = 13) -> str:
    def rotate(c: str) -> str:
        if 'a' <= c <= 'z':
            return chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            return chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
        return c
    return ''.join(rotate(c) for c in text)


print(how(s.strip()))
