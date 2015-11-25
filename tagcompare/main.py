import output
import capture
import compare


def main():
    capture.main()
    output.aggregate()
    compare.do_all_comparisons()


if __name__ == '__main__':
    main()
