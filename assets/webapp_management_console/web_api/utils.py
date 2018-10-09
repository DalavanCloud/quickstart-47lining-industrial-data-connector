from functools import partial, wraps, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
import logging


logger = logging.getLogger(__name__)


wraps_with_injection = partial(wraps, assigned=set(WRAPPER_ASSIGNMENTS) - {'__annotations__'},
                               updated=set(WRAPPER_UPDATES) | {'__annotations__'})
