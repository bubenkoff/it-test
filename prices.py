"""Calculate hotel nightly prices for places."""
import argparse
import collections

from sqlalchemy import create_engine

parser = argparse.ArgumentParser(prog="prices")

parser.add_argument(
        dest="connection_string",
        metavar="CONNECTION_STRING",
        help="Database connection string (mysql://scott:tiger@localhost/foo)",
    )


def main():
    """Print a csv of place_id and nightly price for hotels (filtered)."""
    args = parser.parse_args()
    engine = create_engine(args.connection_string)
    # get initially filtered data from the db
    # the idea of filter is: standard deviation is less than 100 eur, closest to the min of the middle 80% of prices
    # so this will get 'realistic' minimum prices for every location (not yet aggregated fully)
    results = engine.execute("""
        SELECT sq.navigation_path,
               min(Hotel.nightly_price)
        FROM
          ( SELECT Hotel.place_id,
                   Place.navigation_path,
                   max(Hotel.nightly_price) AS max_price,
                   min(Hotel.nightly_price) AS min_price
           FROM Hotel
           JOIN Place ON Place.place_id = Hotel.place_id
           GROUP BY Hotel.place_id HAVING std(Hotel.nightly_price) < 100 ) sq
        JOIN Hotel ON Hotel.place_id = sq.place_id
        WHERE Hotel.nightly_price BETWEEN sq.min_price * 1.1 AND sq.max_price * 0.9
        GROUP BY Hotel.place_id""").fetchall()
    price_by_place_id = collections.defaultdict(float)
    for navigation_path, nightly_price in results:
        # collect mins for every navigation path part
        for place_id in (int(item) for item in reversed(filter(None, navigation_path.split("/")))):
            price_by_place_id[place_id] = min(price_by_place_id[place_id], nightly_price) or nightly_price

    # output a csv header
    print("place_id,price")
    # output a csv body
    for place_id, price in sorted(price_by_place_id.items()):
        print("{0},{1}".format(place_id, price))

if __name__ == '__main__':
    main()
