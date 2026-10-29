import pandas as pd
from app.core import apply_operations, profile, pandas_code

def test_arabic_digits_and_duplicates():
    df=pd.DataFrame({'amount':['١٢٠٫٥٠','SAR 80','SAR 80']})
    out=apply_operations(df,[{'op':'normalize_digits','col':'amount'},{'op':'strip_text','col':'amount','pattern':'SAR'},{'op':'cast_numeric','col':'amount'}])
    assert float(out.iloc[0,0])==120.5
    assert profile(df)['duplicates']==1

def test_code_generation():
    code=pandas_code([{'op':'drop_duplicates','cols':[]}])
    assert 'drop_duplicates' in code and 'to_csv' in code
