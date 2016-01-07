import capture
import compare


def main():
    jobname = capture.main()
    compare.main(build=jobname)


if __name__ == '__main__':
    main()
