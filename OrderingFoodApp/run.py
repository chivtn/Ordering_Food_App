#run.py
from OrderingFoodApp import init_app

app = init_app()

if __name__ == '__main__':
    app.run(port = 5005)
    # app.run(debug=True)

