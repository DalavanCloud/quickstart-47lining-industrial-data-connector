import argparse
import logging

from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def parse_command_line_args():
    parser = argparse.ArgumentParser(description='PI Communication Worker')
    parser.add_argument('--pi_points_table_name', required=True)
    parser.add_argument('--outgoing_sqs_name', required=True)
    parser.add_argument('--events_status_table_name', required=True)
    parser.add_argument('--region', required=True)
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    args = parse_command_line_args()

    feeds_manager = ManagedFeedsManager.create_manager(
        args.region,
        args.pi_points_table_name,
        args.events_status_table_name,
        outgoing_queue_name=args.outgoing_sqs_name
    )

    feeds_manager.start_processing_requests()
