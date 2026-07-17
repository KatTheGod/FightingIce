import pathlib

import constants as c
import functions as f

for log_group_name in c.LOGS.KNOWN_LOGS:
    print(f"Clearing files in log/{log_group_name}")
    f.purge_directory(
        str(pathlib.Path("log").joinpath(log_group_name)),
        remove_root=False,
    )


print("purging custom motions")
f.purge_directory(c.CUSTOM_MOTION_PATH, remove_root=False)

print("purging dask logs")
f.purge_directory(c.LOGS.DASK_LOGS, remove_root=False)

print("purge solution replay logs")
f.purge_directory(pathlib.Path(c.LOGS.SOLUTION_EXPLORER) / "logs")

print("done\n")
