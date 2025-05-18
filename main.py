import time

from driver.images import (analyze_images, clean_up, download_images,
                           dummy_download, set_up)

start = time.perf_counter()

set_up()
url = "https://www.setgame.com/set/puzzle"
# download_images(url)
# dummy_download(url)
analyze_images()

# clean_up()
end = time.perf_counter()
elapsed = end - start
print(f"Total runtime is {elapsed:.2f} seconds.")
