import argparse
import json

pars = argparse.ArgumentParser()
pars.add_argument('--name', '-name', type=str)
pars.add_argument('--data', '-data', type=str)

opt = pars.parse_args()


def fix_str(string: str) -> dict:
    clm = []
    cma = []
    have_https = False
    for i, s in enumerate(string):
        if s == 'h' and string[i + 1] == 't' and string[i + 2] == 't' and string[i + 3] == 'p':
            have_https = True
    values = []
    keys = []
    for i, dot in enumerate(string):
        if dot == ':':
            clm.append(i)
    for i, comma in enumerate(string):
        if comma == ',':
            cma.append(i)
    if have_https:
        clm.pop(-1)
    for i, idx_cl in enumerate(clm):
        values.append(
            string[idx_cl + 1:cma[i] if i != len(cma) else -1] if i != len(clm) - 1 else string[idx_cl + 1:-1])
    for i, idx_cl in enumerate(clm):
        keys.append(string[1:idx_cl] if i == 0 else string[cma[i - 1] + 1:idx_cl])
    for i, (v, k) in enumerate(zip(values, keys)):
        if v[0] == ' ':
            values[i] = v[1:]
        if k[0] == ' ':
            keys[i] = k[1:]
    dct = {}
    for v, k in zip(values, keys):
        dct[k] = v
    return dct


if __name__ == "__main__":
    with open(f'{opt.name}.json', 'w') as w:
        dct = fix_str(opt.data)
        print(dct)
        json.dump(dct, w)
