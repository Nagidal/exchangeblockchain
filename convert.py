#!/usr/bin/env python


from loguru import logger
import source
import target


if __name__ == "__main__":
    for r in source.read_sources():
        logger.info(r)
        d = target.Row(r)
        logger.debug(d)
