from __future__ import annotations
import io, re
from typing import Any
import pandas as pd

ARABIC = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")

def read_table(data: bytes, filename: str, header: int = 0) -> pd.DataFrame:
    stream = io.BytesIO(data)
    if filename.lower().endswith(('.xlsx', '.xls')):
        return pd.read_excel(stream, header=header)
    return pd.read_csv(stream, header=header)

def profile(df: pd.DataFrame) -> dict[str, Any]:
    cols=[]
    for name in df.columns:
        s=df[name]
        cols.append({'name': str(name), 'dtype': str(s.dtype), 'nulls': int(s.isna().sum()), 'unique': int(s.nunique(dropna=True)), 'sample': [str(x) for x in s.dropna().head(3).tolist()]})
    return {'rows': int(len(df)), 'columns': int(len(df.columns)), 'duplicates': int(df.duplicated().sum()), 'columns_profile': cols}

def apply_operations(df: pd.DataFrame, operations: list[dict[str, Any]]) -> pd.DataFrame:
    out=df.copy()
    for op in operations:
        kind=op.get('op')
        col=op.get('col')
        if kind == 'normalize_digits' and col in out:
            out[col]=out[col].astype(str).str.translate(ARABIC)
        elif kind == 'strip_text' and col in out:
            out[col]=out[col].astype(str).str.replace(str(op.get('pattern','')), '', regex=False)
        elif kind == 'drop_duplicates':
            subset=op.get('cols') or None; out=out.drop_duplicates(subset=subset)
        elif kind == 'cast_numeric' and col in out:
            out[col]=pd.to_numeric(out[col].astype(str).str.replace(r'[^0-9.\-]', '', regex=True), errors='coerce')
        elif kind == 'fill_null' and col in out:
            out[col]=out[col].fillna(op.get('value',''))
        else:
            raise ValueError(f'Unsupported operation or column: {op}')
    return out

def suggest_operations(df: pd.DataFrame) -> list[dict[str, Any]]:
    ops=[]
    if df.duplicated().any(): ops.append({'op':'drop_duplicates','cols':[]})
    for c in df.columns:
        values=df[c].dropna().astype(str)
        if values.str.contains(r'[٠-٩]', regex=True).any(): ops.append({'op':'normalize_digits','col':str(c)})
        if values.str.contains(r'\b(?:SAR|ر\.س)\b', regex=True).any(): ops.append({'op':'strip_text','col':str(c),'pattern':'SAR'})
    return ops

def pandas_code(operations: list[dict[str, Any]], input_name='input.csv', output_name='cleaned.csv') -> str:
    lines=["import pandas as pd", f"df = pd.read_csv('{input_name}')"]
    for op in operations:
        kind=op.get('op'); col=op.get('col')
        if kind=='normalize_digits': lines.append(f"df['{col}'] = df['{col}'].astype(str).str.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩٫٬', '0123456789.'))")
        elif kind=='strip_text': lines.append(f"df['{col}'] = df['{col}'].astype(str).str.replace({op.get('pattern','')!r}, '', regex=False)")
        elif kind=='drop_duplicates': lines.append("df = df.drop_duplicates()" if not op.get('cols') else f"df = df.drop_duplicates(subset={op['cols']!r})")
        elif kind=='cast_numeric': lines.append(f"df['{col}'] = pd.to_numeric(df['{col}'].astype(str).str.replace(r'[^0-9.\\-]', '', regex=True), errors='coerce')")
        elif kind=='fill_null': lines.append(f"df['{col}'] = df['{col}'].fillna({op.get('value','')!r})")
    lines += [f"df.to_csv('{output_name}', index=False)"]
    return '\n'.join(lines)+'\n'
