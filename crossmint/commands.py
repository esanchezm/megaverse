#!/usr/bin/env python

import logging
from cleo.commands.command import Command
from cleo.helpers import argument, option
from .api_client import MapClient, PolyanetClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReconcileCommand(Command):
    name = "reconcile"
    description = "Reconcile a map with the expected result."
    arguments = [
        argument(
            "candidate_id",
            description="Candidate ID to reconcile the map for.",
        )
    ]
    options = [
        option(
            "url",
            description="Base API URL to use for reconciliation. Defaults to https://challenge.crossmint.io/",
        ),
    ]

    def handle(self):
        candidate_id = self.argument("candidate_id")

        map_client = MapClient(candidate_id, self.option("url"))
        polyanet_client = PolyanetClient(candidate_id, self.option("url"))

        map_client = MapClient(candidate_id, self.option("url"))
        current_map = map_client.get_status().get("map", {}).get("content", [])
        goal_map = map_client.get_goal().get("goal", [])

        logger.debug(f"Raw goal map: {goal_map}")
        logger.info(f"Reconciling map for candidate {candidate_id}")

        for row in range(len(goal_map)):
            for col in range(len(goal_map[row])):
                if current_map[row][col] is None:
                    current_map[row][col] = "SPACE"

                if current_map[row][col] == goal_map[row][col]:
                    logger.info(f"Map already reconciled at {row}, {col}")
                    continue

                if goal_map[row][col] == "SPACE":
                    logger.info(f"Cleaning polyanet at {row}, {col}")
                    polyanet_client.clean(row, col)
                elif goal_map[row][col] == "POLYANET":
                    logger.info(f"Setting polyanet at {row}, {col}")
                    polyanet_client.set(row, col)
                else:
                    raise RuntimeError(f"Unknown map value: {goal_map[row][col]}")

