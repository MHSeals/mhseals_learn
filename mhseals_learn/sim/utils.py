from typing import Union, List, Tuple, Optional, Callable
from inspect import signature, Parameter
import numpy as np

numeric = Union[int, float]

def generate_rectangle(x: numeric,
                       y: numeric,
                       orientation: numeric,
                       length: numeric,
                       width: numeric,
                       operation: Optional[Callable]=None,
                       *args,
                       **kwargs
                      ) -> List[Tuple[numeric, numeric]]:

    points = []
    diagonal = (length ** 2 + width ** 2) ** (1 / 2)
    a1 = np.arctan2(width, length) * 2
    a2 = np.pi - a1
    angles = [orientation + a1 / 2]
    angles.append(angles[0] + a2)
    angles.append(angles[1] + a1)
    angles.append(angles[2] + a2)

    for i in range(4):
        points.append((
            x + np.cos(angles[i]) * diagonal / 2,
            y + np.sin(angles[i]) * diagonal / 2
        ))
        
    if operation:
        for i, point in enumerate(points):
            points[i] = call_safely(operation, point, *args, **kwargs)
    
    return points
        
def call_safely(func, *args, **kwargs):
    sig = signature(func)
    params = list(sig.parameters.values())

    max_pos = 0
    for p in params:
        if p.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            max_pos += 1
        elif p.kind == Parameter.VAR_POSITIONAL:
            max_pos = len(args)
            break

    filtered_args = args[:max_pos]

    has_var_kw = any(p.kind == Parameter.VAR_KEYWORD for p in params)
    if has_var_kw:
        filtered_kwargs = kwargs
    else:
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

    return func(*filtered_args, **filtered_kwargs)