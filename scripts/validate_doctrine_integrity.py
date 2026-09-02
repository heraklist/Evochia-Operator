#!/usr/bin/env python3
from __future__ import annotations
import hashlib, sys
from pathlib import Path
import yaml

def validate(root: Path) -> list[str]:
    m=yaml.safe_load((root/'references/doctrine_manifest.yaml').read_text(encoding='utf-8'))
    issues=[]
    for item in m['items']:
        p=root/item['target']
        if not p.is_file():
            issues.append(f"missing: {item['target']}")
            continue
        b=p.read_bytes()
        digest=hashlib.sha256(b).hexdigest()
        if digest != item['sha256']:
            issues.append(f"checksum mismatch: {item['target']}")
        if len(b) != item['bytes']:
            issues.append(f"size mismatch: {item['target']}")
    return issues

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    issues=validate(root)
    if issues:
        print('Doctrine integrity: FAIL',file=sys.stderr)
        for x in issues:
            print('- '+x,file=sys.stderr)
        return 1
    count=len(yaml.safe_load((root/'references/doctrine_manifest.yaml').read_text())['items'])
    print(f"Doctrine integrity: PASS ({count} files)")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
