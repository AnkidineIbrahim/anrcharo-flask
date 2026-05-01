from app import create_app, db
from app.models.user import User
from app.models.photo import Photo
from app.models.models import Reservation, Testimonial, Setting

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Photo=Photo,
                Reservation=Reservation, Testimonial=Testimonial, Setting=Setting)

if __name__ == '__main__':
    app.run(debug=True)
