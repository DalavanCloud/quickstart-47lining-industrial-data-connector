import argparse
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def parse_command_line_args():
    parser = argparse.ArgumentParser(description='PI Communication Worker')
    parser.add_argument('--outgoing_sqs_name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--postgres-uri', required=True)
    parser.add_argument('--dts', required=True)
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    args = parse_command_line_args()

    engine = create_engine(args.postgres_uri, use_batch_mode=True)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    feeds_manager = ManagedFeedsManager.create_manager(
        args.region,
        postgres_session=Session,
        outgoing_queue_name=args.outgoing_sqs_name,
        use_iot=True if args.dts == 'AWS IoT' else False
    )

    feeds_manager.start_processing_requests()
