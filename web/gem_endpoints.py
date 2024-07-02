from typing import Dict, List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.auth import AuthHandler
from data.populate import calculate_gem_price
from models.gem_models import Gem, GemProperties, GemTypes, GemPatch
from data.db import get_session, engine



auth_handler = AuthHandler()

gem_router = APIRouter()  # If you want all the endpoints to depend on Gem on something

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@gem_router.get('/gems', tags=['Gems'])
def get_gems(lte: Optional[int] = None, 
             gte: Optional[int] = None, 
             type: List[Optional[GemTypes]] = Query(None), 
             session: Session = Depends(get_session)):
    query = select(Gem, GemProperties).join(GemProperties)
    if lte:
        query = query.where(Gem.price <= lte)
    if gte:
        query = query.where(Gem.price >= gte)
    if type:
        query = query.where(Gem.gem_type.in_(type)).order_by(Gem.gem_type).order_by(~Gem.price).order_by(None)
    gems = session.exec(query).all()
    serialized_gems = [{'gem': jsonable_encoder(gem), 'properties': jsonable_encoder(props)} for gem, props in gems]
    return {'gems': serialized_gems}

@gem_router.get('/gem/{id}', response_model=Gem)
def get_gem(id: int, session: Session = Depends(get_session)):
    gem = session.get(Gem, id)
    if not gem:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Gem not found')
    return jsonable_encoder(gem)

@gem_router.post('/gems', response_model=Gem)
def create_gem(gem_pr: GemProperties, gem: Gem, session: Session = Depends(get_session), user=Depends(auth_handler.get_current_user)):
    """Creates gem"""
    if not user.is_seller:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='This user is not a seller')
    gem_properties = GemProperties(size=gem_pr.size, clarity=gem_pr.clarity, color=gem_pr.color)
    session.add(gem_properties)
    session.commit()
    session.refresh(gem_properties)
    gem.gem_properties_id = gem_properties.id
    gem.seller_id = user.id
    gem.price = calculate_gem_price(gem, gem_pr)
    session.add(gem)
    session.commit()
    session.refresh(gem)
    return jsonable_encoder(gem)

@gem_router.put('/gems/{id}', response_model=Gem)
def update_gem(id: int, gem: Gem, session: Session = Depends(get_session), user=Depends(auth_handler.get_current_user)):
    gem_found = session.get(Gem, id)
    if not gem_found:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Gem not found')
    if not user.is_seller or gem_found.seller_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Can't Modify Content")
    
    update_item_encoded = jsonable_encoder(gem)
    update_item_encoded.pop('id', None)
    for key, val in update_item_encoded.items():
        setattr(gem_found, key, val)
    
    session.add(gem_found)
    session.commit()
    session.refresh(gem_found)
    return jsonable_encoder(gem_found)

@gem_router.patch('/gems/{id}', response_model=Gem)
def patch_gem(id: int, gem_patch: GemPatch, session: Session = Depends(get_session), user=Depends(auth_handler.get_current_user)):
    gem_found = session.get(Gem, id)
    if not gem_found:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Gem not found')
    if not user.is_seller or gem_found.seller_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Can't Modify Content")
    
    update_data = gem_patch.model_dump(exclude_unset=True)
    update_data.pop('id', None)
    for key, val in update_data.items():
        setattr(gem_found, key, val)
    
    session.add(gem_found)
    session.commit()
    session.refresh(gem_found)
    return jsonable_encoder(gem_found)

@gem_router.delete('/gems/{id}', status_code=HTTP_204_NO_CONTENT)
def delete_gem(id: int, session: Session = Depends(get_session), user=Depends(auth_handler.auth_wrapper)):
    gem_found = session.get(Gem, id)
    if not gem_found:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Gem not found')
    if not user.is_seller or gem_found.seller_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Can't Delete Content")
    
    session.delete(gem_found)
    session.commit()
    return JSONResponse(status_code=HTTP_204_NO_CONTENT)

@gem_router.get('/gems/seller/me', tags=['seller'], response_model=List[Dict[str, Union[Gem, GemProperties]]])
def gems_seller(session: Session = Depends(get_session), user=Depends(auth_handler.get_current_user)):
    if not user.is_seller:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    statement = select(Gem, GemProperties).where(Gem.seller_id == user.id).join(GemProperties)
    gems = session.exec(statement).all()
    res = [{'gems': jsonable_encoder(gem), 'props': jsonable_encoder(props)} for gem, props in gems]
    return res
