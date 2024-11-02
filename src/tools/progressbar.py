import tqdm

def pbar(iterable,
         bar_format='{desc} {percentage:3.0f}%|{bar:32}| {n_fmt}/{total_fmt} ({elapsed})',
         color='blue',
         **kwargs):
    return tqdm.tqdm(iterable,bar_format=bar_format,colour=color,**kwargs)
pbar.__doc__ = tqdm.tqdm.__doc__