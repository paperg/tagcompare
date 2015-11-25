import capture
import compare


def main():
    jobname = capture.main()
    compare.main(jobname=jobname)


if __name__ == '__main__':
    main()
