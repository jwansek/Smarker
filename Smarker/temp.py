import assessments
import sys
import os

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        ft1 = f.read()

    with open(sys.argv[2], "r") as f:
        ft2 = f.read()

    similarityMetric = assessments.SimilarityMetric(ft1, ft2, 1, 2)
    print(similarityMetric.get_similarity())
    print(similarityMetric.details)