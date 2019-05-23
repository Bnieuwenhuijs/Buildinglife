from app import db

class Building(db.Model):
    __tablename__ = "Building"

    id                      = db.Column(db.Integer, primary_key=True)    
    building_year           = db.Column(db.Integer)
    building_functionality  = db.Column(db.String(120))
    square_meters           = db.Column(db.Float)
    number_floors           = db.Column(db.Integer)
    total_value             = db.Column(db.Integer)
    steel_quantity          = db.Column(db.Integer)
    steel_Value             = db.Column(db.Integer)
    copper_quantity         = db.Column(db.Integer)
    copper_Value            = db.Column(db.Integer)
    concrete_quantity       = db.Column(db.Integer)
    concrete_Value          = db.Column(db.Integer)
    timber_quantity         = db.Column(db.Integer)
    timber_Value            = db.Column(db.Integer)
    glass_quantity          = db.Column(db.Integer)
    glass_Value             = db.Column(db.Integer)
    polystyrene_quantity    = db.Column(db.Integer)
    polystyrene_Value       = db.Column(db.Integer)

    def __repr__(self):
        return '<Building {}>'.format(self.building_year)