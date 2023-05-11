import argparse
import os
from datetime import datetime

from dotenv import load_dotenv
import utils

from ops_twitter import OperatorTwitter
from ops_article import OperatorArticle
from ops_youtube import OperatorYoutube


parser = argparse.ArgumentParser()
parser.add_argument("--prefix", help="runtime prefix path",
                    default="./run")
parser.add_argument("--start", help="start time",
                    default=datetime.now().isoformat())
parser.add_argument("--run-id", help="run-id",
                    default="")
parser.add_argument("--job-id", help="job-id",
                    default="")
parser.add_argument("--data-folder", help="data folder to save",
                    default="./data")
parser.add_argument("--sources", help="sources to pull, comma separated",
                    default="Twitter,Article,Youtube")
parser.add_argument("--targets", help="targets to push, comma separated",
                    default="notion")
parser.add_argument("--topics-top-k", help="pick top-k topics to push",
                    default=3)
parser.add_argument("--categories-top-k", help="pick top-k categories to push",
                    default=3)
parser.add_argument("--dedup", help="whether dedup item",
                    default=True)


def process_twitter(args):
    print("#####################################################")
    print("# Process Twitter")
    print("#####################################################")
    op = OperatorTwitter()
    data = op.readFromJson(args.data_folder, args.run_id, "twitter.json")
    data_deduped = op.dedup(data, target="toread")
    data_ranked = op.rank(data_deduped)

    targets = args.targets.split(",")
    op.push(data_ranked, targets, args.topics_top_k, args.categories_top_k)
    op.printStats("Twitter", data, data_deduped, data_ranked)


def process_article(args):
    print("#####################################################")
    print("# Process Article")
    print("#####################################################")
    op = OperatorArticle()

    data = op.readFromJson(args.data_folder, args.run_id)
    data_deduped = op.dedup(data, target="toread")
    data_summarized = op.summarize(data_deduped)
    data_ranked = op.rank(data_summarized)

    targets = args.targets.split(",")
    op.push(data_ranked, targets)


def process_youtube(args):
    print("#####################################################")
    print(f"# Process Youtube, dedup: {args.dedup}")
    print("#####################################################")
    op = OperatorYoutube()

    data = op.readFromJson(args.data_folder, args.run_id, "youtube.json")
    data_deduped = data
    need_dedup = utils.str2bool(args.dedup)
    if need_dedup:
        data_deduped = op.dedup(data, target="toread")
    else:
        data_deduped = [x for x in data.values()]

    data_summarized = op.summarize(data_deduped)
    data_ranked = op.rank(data_summarized)

    targets = args.targets.split(",")
    op.push(data_ranked, targets)


def run(args):
    print(f"environment: {os.environ}")
    sources = args.sources.split(",")

    for source in sources:
        print(f"Pushing data for source: {source} ...")

        # Notes: For twitter we don't need summary step
        if source == "Twitter":
            process_twitter(args)

        elif source == "Article":
            process_article(args)

        elif source == "Youtube":
            process_youtube(args)


if __name__ == "__main__":
    args = parser.parse_args()
    load_dotenv()

    run(args)
