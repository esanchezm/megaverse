#!/usr/bin/env python

import logging

from cleo.commands.command import Command
from cleo.helpers import argument, option

from .api_client import (
    Color,
    ComethClient,
    Direction,
    MapClient,
    PolyanetClient,
    SoloonClient,
)

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

    def is_space(self, value: str):
        """
        Check if the value is a space.
        """
        return value == "SPACE"

    def is_polyanet(self, value: str):
        """
        Check if the value is a polyanet.
        """
        return value == "POLYANET"

    def is_soloon(self, value: str):
        """
        Check if the value is a soloon.
        """
        return "_SOLOON" in value

    def is_cometh(self, value: str):
        """
        Check if the value is a cometh.
        """
        return "_COMETH" in value

    def handle(self):
        candidate_id = self.argument("candidate_id")

        map_client = MapClient(candidate_id, self.option("url"))
        polyanet_client = PolyanetClient(candidate_id, self.option("url"))
        soloon_client = SoloonClient(candidate_id, self.option("url"))
        cometh_client = ComethClient(candidate_id, self.option("url"))

        current_map = map_client.get_status().get("map", {}).get("content", [])
        goal_map = map_client.get_goal().get("goal", [])

        logger.debug(f"Raw goal map: {goal_map}")
        logger.info(f"Reconciling map for candidate {candidate_id}")

        for row in range(len(goal_map)):
            for column in range(len(goal_map[row])):
                if current_map[row][column] is None:
                    current_map[row][column] = "SPACE"

                if current_map[row][column] == goal_map[row][column]:
                    logger.info(f"Map already reconciled at {row}, {column}")
                    continue

                if self.is_space(goal_map[row][column]):
                    logger.info(f"Cleaning {row}, {column}")
                    polyanet_client.clean(row, column)
                    soloon_client.clean(row, column)
                    cometh_client.clean(row, column)
                elif self.is_polyanet(goal_map[row][column]):
                    logger.info(f"Setting polyanet at {row}, {column}")
                    polyanet_client.set(row, column)
                elif self.is_soloon(goal_map[row][column]):
                    color = Color(goal_map[row][column].split("_")[0].lower())
                    logger.info(
                        f"Setting soloon at {row}, {column} with color {color.value}"
                    )
                    soloon_client.set(row, column, color)
                elif self.is_cometh(goal_map[row][column]):
                    direction = Direction(goal_map[row][column].split("_")[0].lower())
                    logger.info(
                        f"Setting cometh at {row}, {column} with direction {direction.value}"
                    )
                    cometh_client.set(row, column, direction)
                else:
                    logger.error(
                        f"Unknown map value: {goal_map[row][column]}, skipping"
                    )
