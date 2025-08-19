#run.py
from OrderingFoodApp import init_app

app = init_app()

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

