from numpy import array as numpy_array
from numpy import dot as numpy_dotproduct

from pandas import DataFrame as pandas_dataframe

from flask import Flask, request
from flask_cors import CORS

from json import dumps as jsondumps

from redis import StrictRedis as redis


def GETconnection():
    """
    Open up the connection to the Redis store.
    Note: Need to put this into a config file.
    """

    return redis(host='somewhere',
                 port=6379,
                 db=0,
                 password='somepasswd',
                 ssl=False)


def make_numpy_array(factor_matrix):
    """
    Takes the collection of strings representing each of the restaurant
    factor vectors and puts them together in a numpy array for fast
    vectorised calculations late on.

    An alternative (neater) function could be:

    def make_numpy_array(factor_matrix):

        hello = list(map(lambda x: x.decode(), resto_factors.values()))
        hello = list(map(lambda x: x[1:-1].split(','),hello))
        hello = list(map(lambda x: [float(y) for y in x], hello))

        return hello
    """

    func1 = lambda x: x.decode()
    func2 = lambda x: x[1:-1].split(',')
    func3 = lambda x: list(map(float, x))

    nparr = numpy_array(
        list(
            map(func3,
                map(func2,
                    map(func1, factor_matrix.values())
                    )
                )
        )
    )

    return nparr


def serve_products(user, outcode, num_products):
    """
    Takes as arguments the user_id and postcode_district along with the
    number of restaurants that are to be recommended, and returns these
    restaurant recommendations as a dictionary/json.

    """

    userpcd_name = 'POSTCODE_USER_MATRIX:' + outcode
    pcdresto_name = 'POSTCODE_RESTO_MATRIX:' + outcode

    user_factor = conn.hget(userpcd_name, user)
    resto_factors = conn.hgetall(pcdresto_name)

    # We have to be careful when doing this with the key and values. We should
    # try to have these in lock and step. Use module COLLECTIONS and use
    # OrderDict
    resto_factor_matrix = make_numpy_array(resto_factors)
    resto_ids = [restaurant.decode() for restaurant in resto_factors.keys()]

    user_vector = list(
        map(lambda x: float(x), user_factor.decode()[1:-1].split(',')))
    user_vector = numpy_array(user_vector).reshape(len(user_vector), 1)

    recommendations = pandas_dataframe(data=numpy_dotproduct(resto_factor_matrix, user_vector),
                                       index=resto_ids,
                                       columns=['rank']) \
        .sort_values('rank', ascending=False) \
        .head(num_products)

    # Put the following in a sepearte function called get restaurants. Remember to keep the order. 

    reco = '{'

    for n in list(recommendations.index):
        reco = reco + '"' + n + '"' + ':' + jsondumps(eval(conn.get('RESTO_METADATA:' + n).decode())) + ','

    reco = reco[:-1] + '}'

    return reco


conn = GETconnection()

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_restos():
    """
    Function which defines the recommendation endpoint
    """

    user = request.args.get('user')
    pcdistrict = request.args.get('pcdistrict')

    values = serve_products(user, pcdistrict, 5)

    return values


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
