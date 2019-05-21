from app import db

class Building(db.Model):
    __tablename__ = "Building"

    id                      = db.Column(db.Integer, primary_key=True)    
    building_year           = db.Column(db.Integer)
    building_functionality  = db.Column(db.String(120))
    square_meters           = db.Column(db.Float)
    number_floors           = db.Column(db.Integer)


    def __repr__(self):
        return '<Building {}>'.format(self.building_functionality) 

