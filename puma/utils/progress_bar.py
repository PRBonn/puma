from tqdm import trange


def print_progress(pbar, idx, n_scans):
    msg = "[scan #{0}] Integrating scan #{0} of {1}".format(idx, n_scans)
    pbar.set_description(msg)
    return len(msg)


def get_progress_bar(first_scan, last_scan):
    return trange(
        first_scan,
        last_scan,
        unit=" scans",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}[{elapsed}<{remaining}, {rate_fmt}{postfix}]",
    )
