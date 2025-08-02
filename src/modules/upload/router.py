
from typing import List
from fastapi import  UploadFile, File, HTTPException, APIRouter
from cloudinary.uploader import upload as cloud_upload
from src.config.cloudinary import cloudinary
from src.utils.response import CustomResponse as cr

router = APIRouter()

@router.post("/files")
async def upload_multiple(
    files: List[UploadFile] = File(...),
):
    results = []    
    for upload in files:
        try:
            content = await upload.read()  # bytes
            resp = cloud_upload(
                content,
                resource_type="auto",
            )
            results.append({
                "filename": upload.filename,
                "content_type": upload.content_type,
                "size": len(content),
                "url": resp.get("secure_url"),
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed for {upload.filename}: {str(e)}")
    return cr.success(data={"files": results})