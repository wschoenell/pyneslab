__author__ = 'william'


def chiller_control(argv):

    print argv


def chiller_cacti(argv):
    """
    Simple script to read variables and print on cacti (http://www.cacti.net/) script output format for plotting
    """

    if len(argv) < 3:
        print('Usage: %s port var1 var2 ...')

    chiller = NeslabChiller(sys.argv[1])

    for var in argv[2:]:
        chiller.


