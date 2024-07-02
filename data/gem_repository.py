from data.db import session, engine 
from models.gem_models import Gem, GemProperties
from sqlmodel import Session, or_, select


def select_all_gems():
  with Session(engine) as session:
    statement = select(Gem, GemProperties).join(GemProperties)
    # statement = statement.where(Gem.id > 0).where(Gem.id < 2)
    # statement = statement.where(or_(Gem.id>1, Gem.price!=2000))

    result = session.exec(statement)
    res = []
    for gem, props in result:
      res.append({'gem': gem, 'props': props})
    # print(result.all())
    return res
  

# def select_gem(id):
#   with Session(engine) as session:
#     statement = select(Gem).join(GemProperties)
#     # statement = statement.where(Gem.id > 0).where(Gem.id < 2)
#     # statement = statement.where(or_(Gem.id>1, Gem.price!=2000)) 
#     statement = statement.where(Gem.id == id)

#     result = session.exec(statement)
#     return result.first()
  
def select_gem(id: int):
    with Session(engine) as session:
        statement = select(Gem).join(GemProperties)
        result = session.exec(statement)
        gem = result.first()
        if gem:
            return gem
        else:
            return None


# select_gems()