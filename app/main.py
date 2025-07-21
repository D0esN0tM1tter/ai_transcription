from fastapi import FastAPI 
from app.api.routers.pipeline_router import router as pipeline_router 

app = FastAPI() 

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# registering thr router in the app :
app.include_router(pipeline_router , prefix="/api" , tags=["pipeline"]) 

@app.get("/") 
def root() :
    return {"status" : "API is running"}