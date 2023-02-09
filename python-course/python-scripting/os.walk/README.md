## Search from the current working dir
```py
import os
for root, dirs, files in os.walk("."):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))
```

## Search from root file system
```py
import os
for root, dirs, files in os.walk("/"):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))
```

## Search from a specific path
```py
import os
for root, dirs, files in os.walk("/home/s5tia"):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))

import os
PATH = "/home/s5tia"
for root, dirs, files in os.walk(PATH):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))
```

## Print all s5tia dir
```py
import os


def get_all_tomcats():
    list_of_config_dirs = []
    for r, d, f in os.walk("/"):
        for each_dir in d:
            if each_dir == 's5tia':
                list_of_config_dirs.append(os.path.join(r, each_dir))
                print(list_of_config_dirs)

    return None


get_all_tomcats()
```