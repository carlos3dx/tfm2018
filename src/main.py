import sys

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)


def main():
    tweets_path = "./data/Trump/WashingtonGeoTime_Trump.json"


if __name__ == '__main__':
    main()
    print("Finished")
    sys.exit(0)
