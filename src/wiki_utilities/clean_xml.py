import sys
import re


def clean_xml(input, output):
    p_category = re.compile(r'\[\[Category')
    p_tags = re.compile(r"[<>]")

    fout = open(output, "w")

    with open(input, 'r') as file:
        for line in file:
            if re.search(p_tags, line) or re.search(p_category, line):
                fout.write(line)

    fout.close()


if __name__ == '__main__':
    clean_xml("/home/cvillarl/Documents/tfm/enwiktionary-20171220-pages-articles-multistream.xml",
              "/home/cvillarl/Documents/tfm/enwiktionary-20171220-pages-articles-multistream_clean.xml")
    print("Finished")
    sys.exit(0)
