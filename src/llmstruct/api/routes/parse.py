from fastapi import APIRouter, Depends, HTTPException
from ..models import ParseRequest, ParseResponse
from ..deps import get_api_key
from llmstruct.core.parse import parse_codebase

router = APIRouter()

@router.post("/parse", response_model=ParseResponse)
async def parse_endpoint(req: ParseRequest, api_key: str = Depends(get_api_key)):
    struct = parse_codebase(
        root_dir=req.root_dir,
        output=req.output,
        language=req.language,
        include=req.include,
        exclude=req.exclude,
        include_dir=req.include_dir,
        exclude_dir=req.exclude_dir,
        include_ranges=req.include_ranges,
        include_hashes=req.include_hashes,
        goals=req.goals,
        use_cache=req.use_cache,
        modular_index=req.modular_index,
    )
    return ParseResponse(struct=struct) 