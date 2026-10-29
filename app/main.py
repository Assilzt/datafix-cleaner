from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from .core import read_table, profile, apply_operations, suggest_operations, pandas_code

app=FastAPI(title='DataFix Cleaner', version='0.1.0')
class OperationRequest(BaseModel): operations: list[dict]

@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/profile')
async def profile_file(file: UploadFile=File(...)):
    df=read_table(await file.read(), file.filename or 'input.csv'); return {'profile':profile(df),'suggestions':suggest_operations(df)}
@app.post('/clean')
async def clean_file(file: UploadFile=File(...), request: OperationRequest=None):
    df=read_table(await file.read(), file.filename or 'input.csv')
    try: cleaned=apply_operations(df, (request.operations if request else suggest_operations(df)))
    except ValueError as e: raise HTTPException(400, str(e))
    return Response(cleaned.to_csv(index=False), media_type='text/csv', headers={'Content-Disposition':'attachment; filename=cleaned.csv'})
@app.post('/code')
def code(request: OperationRequest): return {'code':pandas_code(request.operations)}
