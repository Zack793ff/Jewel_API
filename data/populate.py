import random
from sqlmodel import Session
from data.db import engine
from models.gem_models import Gem, GemColor, GemProperties, GemTypes

color_multiplier = {
    'D': 1.0,
    'E': 1.6,
    'G': 1.4,
    'F': 1.2,
    'W': 1,
    'I': 0.8
}

def calculate_gem_price(gem, gem_pr):
    price = 1000
    if gem.gem_type == 'Ruby':
        price = 400
    elif gem.gem_type == 'Emerald':
        price = 650

    if gem_pr.clarity == 1:
        price *= 0.75
    elif gem_pr.clarity == 3:
        price *= 1.25
    elif gem_pr.clarity == 4:
        price *= 1.5

    price *= (gem_pr.size**3)

    if gem.gem_type == 'DIAMOND':
        multiplier = color_multiplier.get(gem_pr.color, 1)
        price *= multiplier

    return price

def create_gem_props():
    size = random.randint(3, 70) / 10
    color = random.choice(list(GemColor))
    clarity = random.randint(1, 4)

    gem_p = GemProperties(size=size, clarity=clarity, color=color)
    return gem_p

def create_gem(gem_p):
    gem_type = random.choice(list(GemTypes))
    gem = Gem(price=1000, gem_properties_id=gem_p.id, gem_type=gem_type)
    price = calculate_gem_price(gem, gem_p)
    price = round(price, 2)
    gem.price = price
    return gem


def create_gems_db():
    gem_ps = [create_gem_props() for _ in range(100)]
    with Session(engine) as session:
        session.add_all(gem_ps)
        session.commit()
        for gem_p in gem_ps:
            session.refresh(gem_p)  # To update gem_p with its ID after commit
        gems = [create_gem(gem_p) for gem_p in gem_ps]
        session.add_all(gems)
        session.commit()

# create_gems_db()
